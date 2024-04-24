import os
from kserve import constants
from kserve import V1beta1InferenceService
from kserve import V1beta1InferenceServiceSpec
from kserve import V1beta1PredictorSpec
from kserve import V1beta1ModelSpec
from kserve import V1beta1ModelFormat
from kserve import V1beta1StorageSpec
from urllib.parse import urlparse

import json
import matplotlib.pyplot as plt
import requests
import time
from kubernetes import client


def create_data_connection_secret(selected_model):
    """
    Creates a manifest file to model the Secret representing an ODH DataConnection to the
    S3 bucket.
    """
    connection_secret = f'''
kind: Secret
apiVersion: v1
metadata:
  name: {selected_model.name}-s3-creds
  namespace: {os.environ['MODEL_NAMESPACE']}
  labels:
    opendatahub.io/dashboard: 'true'
    opendatahub.io/managed: 'true'
  annotations:
    opendatahub.io/connection-type: s3
    openshift.io/display-name: {selected_model.name}-s3
stringData:
  AWS_ACCESS_KEY_ID: {os.environ['accesskey']}
  AWS_DEFAULT_REGION: {os.environ['AWS_DEFAULT_REGION']}
  AWS_S3_BUCKET: {os.environ['AWS_S3_BUCKET']}
  AWS_S3_ENDPOINT: {os.environ['AWS_S3_ENDPOINT']}
  AWS_SECRET_ACCESS_KEY: {os.environ['secretkey']}
type: Opaque
'''

    with open("connection_secret.yaml", 'w') as file:
        file.write(connection_secret)


def create_inference_service(selected_model, selected_model_version, selected_model_artifact):
    """
    Creates an InferenceService manifest to model the selected Model version and artifact.

    Returns the InferenceService instance
    """
    # Normalize name v.simple_NN.20240419150600 to comply with DNS naming specs
    model_name = selected_model_version.name.lower().split(".")[1].replace("_", "-")
    os.environ['MODEL_NAME'] = model_name
    kserve_version = 'v1beta1'
    api_version = constants.KSERVE_GROUP + '/' + kserve_version
    namespace = os.environ['MODEL_NAMESPACE']
    s3_secret_name = f"{selected_model.name}-s3-creds"
    # service_account_name = f"{selected_model.name}-s3-creds"
    # s3://feast/v.simple_NN.20240419150600/simple_NN.onnx?endpoint=http://minio-service.feast.svc.cluster.local:9000&defaultRegion=default
    storage_path = urlparse(selected_model_artifact.uri).path.lstrip('/')
    model_format_name = selected_model_artifact.model_format_name
    model_format_version = selected_model_artifact.model_format_version
    storage_uri = selected_model_artifact.uri.split("?")[0]

    inference_service = V1beta1InferenceService(api_version=api_version,
                                                kind=constants.KSERVE_KIND,
                                                metadata=client.V1ObjectMeta(
                                                    name=model_name, namespace=namespace,
                                                    annotations={'serving.kserve.io/deploymentMode': 'ModelMesh'},
                                                    labels={'modelregistry.opendatahub.io/registered-model-id': selected_model.id,
                                                            'modelregistry.opendatahub.io/model-version-id': selected_model_version.id,
                                                            'opendatahub.io/dashboard': 'true', }
                                                 ),
                                                spec=V1beta1InferenceServiceSpec(
                                                    predictor=V1beta1PredictorSpec(
                                                       model=V1beta1ModelSpec(
                                                           name=model_name,
                                                           storage=V1beta1StorageSpec(
                                                               key=s3_secret_name,
                                                               path=storage_path,
                                                           ),
                                                           model_format=V1beta1ModelFormat(name=model_format_name, version=model_format_version),
                                                           runtime="mnist",
                                                           # protocol_version='v2'
                                                           # see https://kserve.github.io/website/master/modelserving/v1beta1/onnx/#create-the-inferenceservice
                                                        ))))
    print(f"Creating InferenceService {inference_service.metadata.name} to serve {storage_uri}")
    return inference_service


def delete_existing_inference_service(KServe, inference_service):
    """
    Deletes an instance of the givenInferenceService from the KServe cluster
    """
    try:
        KServe.get(inference_service.metadata.name, inference_service.metadata.namespace)
        print(f"Deleting existing service with name {inference_service.metadata.name}")
        KServe.delete(inference_service.metadata.name, inference_service.metadata.namespace)
    except RuntimeError:
        print("No existing service to delete")


def wait_until_predictor_is_ready(KServe, inference_service):
    """
    Wait until the predictor of the given instance of InferenceService is ready.
    Maximum timeout of 3 minutes, check the state every 3 seconds.
    """
    model_name = inference_service.metadata.name
    model_namespace = inference_service.metadata.namespace
    print(f"Waiting until model {model_name} is ready")

    total_iterations = 5 * 60 // 3
    iteration = 0
    is_predictor_ready = False
    while iteration < total_iterations:
        inference_service = KServe.get(model_name, model_namespace)
        if 'status' in inference_service and 'conditions' in inference_service['status']:
            is_predictor_ready = \
                bool([condition['status'] for condition in inference_service['status']['conditions'] if condition['type'] == 'PredictorReady'][0]) | False
            if is_predictor_ready is True:
                break

        iteration += 1
        time.sleep(3)

    if is_predictor_ready:
        print(f"Predictor is ready for {model_name}")
    else:
        print(f"Predictor is not ready for {model_name}")


def inference_service_uris(KServe, inference_service):
    """
    Returns the REST, model and prediction URI of the given InferenceService instance
    """
    model_name = inference_service.metadata.name
    model_namespace = inference_service.metadata.namespace
    inference_service = KServe.get(model_name, model_namespace)
    rest_uri = inference_service['status']['components']['predictor']['restUrl']
    model_service_uri = f"{rest_uri}/v2/models/{model_name}"
    prediction_uri = f"{model_service_uri}/infer"
    return (rest_uri, model_service_uri, prediction_uri)


def inspect_service_metadata(model_service_uri):
    """
    Given the model service URI of the InferenceService, returns the published metadata to query the service for
    predictin purposes (see 'inputs' and 'outputs' fields)
    """
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.get(model_service_uri, headers=headers)
    if response.status_code == 200:
        output_data = response.json()
        print(f"Metadata request to {model_service_uri} succeded.")
        return output_data
    else:
        print(f"Metadata request to {model_service_uri} failed with status code: {response.status_code}")


def generate_prediction_input(model_name, image):
    """
    Generates the prediction input dictionary for the given image, according to
    the required format
    """
    prediction_input = {
        "model_name": model_name,
        "inputs": [{
            "name": "x",
            "shape": [1, 28, 28],
            "datatype": "FP64",
            "data": []
        }]
    }

    prediction_input['inputs'][0]['data'] = image
    return prediction_input


def validate_prediction(inference_service, prediction_uri, image_id, image):
    """
    Given the InferenceService, the image_id and the image data, validates the prediction against the service.
    The expectation is that the predicted value matches the given image_id.
    It also plots the image for visual validation
    """
    headers = {
        'Content-Type': 'application/json'
    }

    prediction_input = generate_prediction_input(inference_service.metadata.name, image)
    response = requests.post(prediction_uri, data=json.dumps(prediction_input), headers=headers)
    if response.status_code == 200:
        output_data = response.json()
        predictions = output_data['outputs'][0]['data']
        max_prediction = max(predictions)
        max_index = predictions.index(max_prediction)
        print(f"The predicted number for image {image_id} is {max_index}")
        plt.figure(figsize=(1, 1))
        plt.imshow(image[0], cmap=plt.get_cmap('gray'))
        plt.show()
        assert max_index == image_id, f"The prediction failed: expected {image_id}, predicted {max_index}"
    else:
        # with open("data.json", 'w') as file:
        #     file.write(json.dumps(prediction_input))
        print(f"POST request to {prediction_uri} for {prediction_input} failed with status code: {response.status_code}")