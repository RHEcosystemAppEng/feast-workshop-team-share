from model_registry import ModelRegistry
from model_registry.types import ContextState

# The ModelRegistry host
model_registry_host = "modelregistry-sample.feast.svc.cluster.local"
# The ModelRegistry REST port
model_registry_port = 9090


def get_model_registry():
    """
    The ModelRegistry instance
    """
    return ModelRegistry(server_address=model_registry_host, port=model_registry_port, author="feast-dev@redhat.com")


def select_model_for_test():
    """
    Select the first model, version and artifact available from the ModelRegistry (excluding
    the ARCHIVED versions).
    Returns the tuple (selected_model, selected_model_version, selected_model_artifact)
    """
    registry = get_model_registry()

    models = registry._api.get_registered_models()
    for model in models:
        print(f"Model {model.name}")
        model_versions = registry._api.get_model_versions(model.id)
        for model_version in model_versions:
            print(f"Version {model_version.name}")
            model_artifacts = registry._api.get_model_artifacts(model_version.id)
            for model_artifact in model_artifacts:
                print(f"Artifact {model_artifact.name}: {model_artifact.uri}")

    # Update the logic to select the model and the version
    selected_model = models[0]
    live_model_versions = [m for m in registry._api.get_model_versions(selected_model.id) if m.state != ContextState.ARCHIVED]
    selected_model_version = live_model_versions[0]
    selected_model_artifact = registry._api.get_model_artifacts(selected_model_version.id)[0]
    return (selected_model, selected_model_version, selected_model_artifact)