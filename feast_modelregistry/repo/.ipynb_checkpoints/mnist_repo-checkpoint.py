from datetime import timedelta

import pandas as pd

from feast import Entity, FeatureService, FeatureView, Field, PushSource, RequestSource
from feast.infra.offline_stores.contrib.postgres_offline_store.postgres_source import (
    PostgreSQLSource,
)
from feast.on_demand_feature_view import on_demand_feature_view
from feast.types import Float32, Float64, Int64, Array

image = Entity(name="image", join_keys=["image_id"])

mnist_source = PostgreSQLSource(
    name="mnist_source",
    query="SELECT * FROM mnist_source",
    timestamp_field="ts",
    created_timestamp_column="created",
)

features = [Field(name=f"feature_{i+1}", dtype=Array(Float32)) for i in range(28)]
features = features.append(Field(name="number", dtype=Int64))
mnist_fv = FeatureView(
    name="mnist",
    entities=[image],
    ttl=timedelta(days=10),
    schema=features,
    online=True,
    source=mnist_source,
    tags={"team": "redhat_feast", "demo": "mnist"},
)

mnist = FeatureService(
    name="mnist",
    features=[
        mnist_fv[[f"feature_{i+1}" for i in range(28)]],
    ],
)

images_push_source = PushSource(
    name="images_push_source",
    batch_source=mnist_source,
)

mnist_fresh_fv = FeatureView(
    name="mnist_fresh",
    entities=[image],
    ttl=timedelta(days=10),
    schema=features,
    online=True,
    source=images_push_source,
    tags={"team": "redhat_feast", "demo": "mnist"},
)