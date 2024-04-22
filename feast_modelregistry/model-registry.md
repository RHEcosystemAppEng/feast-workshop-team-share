# Reference deployment of Model Registry
* Clone `model-registry-operator` repo:
```console
git clone https://github.com/opendatahub-io/model-registry-operator.git
```
* Install the CRDs:
```console
cd model-registry-operator
make install
```
* Install the operator in the default `model-registry-operator-system` namespace:
```console
IMG_VERSION=v0.1.3 make deploy
```
* Configure a sample `ModelRegistry` instance with PSQL and no Istio in the `feast` namespace:
```console
oc project feast
OVERLAY=samples/postgres make deploy
```