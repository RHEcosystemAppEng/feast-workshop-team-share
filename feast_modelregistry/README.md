# MNIST Demo with <img src="https://docs.feast.dev/~gitbook/image?url=https:%2F%2F2070487677-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-legacy-files%2Fo%2Fspaces%252F-LqPPgcuCulk4PnaI4Ob%252Favatar-rectangle-1590217195988.png%3Fgeneration=1590217197437042%26alt=media&width=192&dpr=1&quality=100&sign=0a0c387ee7d229ceed344e4be41be8d1ec300df3dbb901293ba4235f43174373" alt="FEAST" style="height:30px;"> and Model Registry <img src="https://avatars.githubusercontent.com/u/33164907?s=200&v=4" alt="Model Registry" style="height:30px;"> in RHOAI <img src="images/RHOAI.png" alt="Model Registry" style="height:30px;">

Purpose of this demo is to replicate the [Model Registry](https://github.com/opendatahub-io/model-registry) demos that use the
[MNIST dataset](https://en.wikipedia.org/wiki/MNIST_database) to predict numbers from digital images introducing
[FEAST](https://docs.feast.dev/) as the Feature Store in a [Red Hat OpenShift AI (RHOAI)](https://www.redhat.com/en/technologies/cloud-computing/openshift/openshift-ai) environment.

Link to original demos (YouTube video and git repo):
* [Model Registry (alpha) progress demo 20240309](https://www.youtube.com/watch?v=JVxUTkAKsMU), [demo20240309-mrvanillakf](https://github.com/tarilabs/demo20240309-mrvanillakf)
* [Model Registry tech demo 20231121 e2e](https://www.youtube.com/watch?v=grXnjGtDFXg), [demo20231121](https://github.com/tarilabs/demo20231121)

## Demo Architecture
![](./images/DemoArchitecture.jpg)

## Demo Notebooks
### Prerequisites
* PSQL DB instance created
    * Note: at least `1Gi` of memory is requested, especially if you run in ephemeral mode
* Model Registry operator installed and PSQL instance created
    * A [reference deployment](./model-registry.md) is available for your convenience
* S3-compatible server and `feast` bucket available
    * Use [MinIO](https://min.io/), installed with these [instructions](https://ai-on-openshift.io/tools-and-applications/minio/minio/)

### RHOAI Configuration
We assume that the following configuration exists before executing the demo notebooks:
* A `Data Science Project` called `feast`
* A `Model Server`called `mnist` in the `feast` project
* A `Data Connection` called `mnist-s3-creds` created to model the above mentioned S3 bucket

Use the following command to automatically create the `Data Connection` from the provided manifest [connection-secret.yaml](./connection-secret.yaml):
```console
oc apply -f connection-secret.yaml
```

* A `Workbench` running `TensorFlow` image: notebooks have been validated with version `2023.2`
    * Connect the `Workbench` with the previously created `Data Connection` to automatically inject the secret keys as environment variables

Once the workbench is started, import the notebookes by cloning the git repo at `https://github.com/RHEcosystemAppEng/feast-workshop-team-share.git`. 

### Data Collection and Preparation
* [00-persist-mnist.ipynb](./00-persist-mnist.ipynb)
* [01-setup-feast.ipynb](./01-setup-feast.ipynb)

![](./images/DataPreparation.jpg)

### Model Training
* [02-training-and-register-mr.ipynb](./02-training-and-register-mr.ipynb)
![](./images/ModelTrainingAndRegistration.jpg)

### Online Features: predict from Inference Service
* [03-push-online-data.ipynb](./03-push-online-data.ipynb)
* [04-inference-service.ipynb](./04-inference-service.ipynb)
![](./images/ModelTrainingAndRegistration.jpg)

## Next steps
* Adopt `Istio` based deployment of Model Registry (see [Istio Configuration](https://github.com/opendatahub-io/model-registry-operator/blob/main/README.md#istio-configuration))
* Adopt the `Data Connection` approach to connect the SQL database:
    * RHOAI has plans to allow many instances for a single workbench
    * An alternative to consider is the Kubeflow's [PodDefault](https://github.com/kubeflow/kubeflow/tree/v1.3.1-rc.0/components/admission-webhook)
    in case it will be integrated in RHOAI


