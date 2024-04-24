import os

from feast import FeatureStore


def fetch_online_features():
    """
    Fetch the online features of the Feast repo.
    Return a (reshuffled) DataFrame
    """
    store = FeatureStore(repo_path=os.environ['REPO_PATH'])
    online_features = store.get_online_features(
        features=[f"mnist_fresh:feature_{feature_id+1}" for feature_id in range(28)],
        entity_rows=[{"image_id": f"{image_id}"} for image_id in range(10)]
    ).to_df()

    # Reshuffle dataframe with random order
    online_features = online_features.sample(frac=1, random_state=42)
    return online_features


# Translates string array of floats to list of floats
def to_array(float_array_string):
    """
    Return a list of floats corresponding to its stringified version provided as input argument.
    """
    return float_array_string
    # return [float(x) for x in float_array_string.strip('()').split(',')]


def to_model_data(online_features):
    """
    Given a DataFrame representing the online features, return a 3D array where each entry is the original 28x28
    matrix from the MNIST database
    """
    image_ids = []
    images = []
    for index in range(len(online_features)):
        image_ids.append(online_features['image_id'].iloc[index])

        image = []
        image.append([to_array(online_features[f'feature_{id+1}'].iloc[index]) for id in range(28)])
        images.append(image)
    return (image_ids, images)