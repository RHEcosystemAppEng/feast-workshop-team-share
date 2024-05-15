# Feast Offline store with Arrow Flight - an investigation

Purpose of this POC is to validate a solution to implement the issue [Remote offline feature server deployment](https://github.com/feast-dev/feast/issues/4032) using [Arrow Flight](https://arrow.apache.org/blog/2019/10/13/introducing-arrow-flight/) server as the remote Feast offline store.

## Prerequisites
The POC is based on the MNIST Feast store defined by the [MNIST Demo](../feast_modelregistry/README.md), so you should run at least
the first 2 notebooks to generate the Feast Repository at `../feast_modelregistry/mnist_demo/feature_repo/` and populate the Feast MNIST dataset
in the associated DB.

Otherwise, the notebooks can easily be adapted to manage offline store of any other Feast repository.

## Architecture
The [ArrowServer](./ArrowServer.ipynb) notebook emulates a Feast store launched using the `feast server_offline` command that will be
introduced as part of this new feature.
* Spins up an Arrow Flight server at port 8815
* The server accepts `do_get` requests for the `get_historical_features` command and delegates the implementation to the associated 
Feast `FeatureStore` (initialized from the above path)

The [ArrowClient](./ArrowClient.ipynb) notebook defines a `RemoteOfflineStore` implementation of the Feast `OfflineStore` interface 
using the remote server as the actual data provider.
* Implements only the `get_historical_features` method
* Since the implementation is lazy, the returned `RetrievalJob` does not run the `do_get` request until any method to synchronously execute
the underlying query is invoked (e.g., `to_df` or `to_arrow`)

## Data exchange protocol
The Apache Arrow Flight protocol defines generic APIs for efficient data streaming to and from the server, leveraging the gRPC communication framework.

The server exposes services to retrieve or push data streams associated with a particular `Flight` descriptor, using the `do_get` and `do_put` endpoints,
but the APIs are not sufficiently detailed for the use that we have in mind, e.g. **adopt the Arrow Flight server as a generic gRPC server
to serve the Feast offline APIs**.

Each API in the `OfflineStore` interface has multiple parameters that has to be transferred to the server to perform the actual implementation.
The way we implement the data transfer protocol is the following:
* The client, e.g. the `RemoteOfflineStore` instance, receives a call to the `get_historical_features` API with the required parameters 
(e.g., `entity_df` and `feature_refs`)
* The client creates a unique identifier for a new command, using the UUID format, and generates a `Flight Descriptor` to represent it
* Then the client sends the received API parameters to the server using multiple calls to the `do_put` service
  * Each call includes the streamed value of the parameter.
  * Each call also includes additional metadata values to the data schema:
      * A `command` metadata with the unique command identifier calculated before.
      * An `api` metadata with the name of the API to be invoked remotely, e.g. `get_historical_features`.
      * A `param` metadata with the name of each parameter of the API.
* When the server receives the `do_put` calls, it stores the data in memory, using an ad-hoc `flights` dictionary indexed by the unique 
`command` identifier and storing a document with the streamed metadata values:
```json
{
    "(b'8d6a366a-c8d3-4f96-b085-f9f686111815')": {
        "command": "8d6a366a-c8d3-4f96-b085-f9f686111815",
        "api": "get_historical_features",
        "entity_df": ".....",
        "features": "...."
    }
}
```
* Having a flight descriptor indexed by unique `command` identifier, allows us to serve multiple clients connected to the same server and
requesting the same service at the same time, with no overlaps.
* Since the client implementation is lazy, the returned instance of `RemoteRetrievalJob` invokes the `do_get` service on the server only when
the data is requested, e.g. in the `_to_arrow_internal` method.
* When the server receives the `do_get` request, it unpacks the API parameters from the `flights` dictionary and, if the requested API is
set to `get_historical_features`, forwards the request to the internal instance of `FeatureStore`.
* Once the `do_get` request is consumed, the associated flight is removed from the `flights` dictionary, as we do not expect the same 
API request to be executed twice from any client.

Other APIs of the `OfflineStore` interface can be implemented the same way, assuming that both the client and the server implementation 
agree on the data exchange protocol to be used to let the server execute the service remotely.

As an alternative, APIs that do not have any returned data may be implemented as a `do_action` service in the server.

