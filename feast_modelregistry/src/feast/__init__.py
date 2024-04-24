import os


def init():
    """
    Initialize the Feast environment
    """

    # Namespace where the model is deployed
    # Change this variable to use a different `Data Science Project`
    os.environ['MODEL_NAMESPACE'] = 'feast'
    # Relative path to the Feast repository
    os.environ['REPO_PATH'] = 'mnist_demo/feature_repo/'
    # Disable Feast usage reporting
    os.environ['FEAST_USAGE'] = 'False'
    print(f"Initialized Feast environment for repo {os.environ['REPO_PATH']}")


init()