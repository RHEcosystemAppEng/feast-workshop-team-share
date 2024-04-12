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

## Data Preparation
* [00-persist-mnist.ipynb](./00-persist-mnist.ipynb)
* [01-setup-feast.ipynb](./01-setup-feast.ipynb)

![](./images/DataPreparation.jpg)

## Demo Architecture
* [02-training-and-register-mr.ipynb](./02-training-and-register-mr.ipynb)
![](./images/ModelTrainingAndRegistration.jpg)


