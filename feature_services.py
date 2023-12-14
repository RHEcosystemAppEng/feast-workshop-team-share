from feast import FeatureService

from features import *

feature_service = FeatureService(
    name="model_v1",
    features=[driver_hourly_stats_view[["conv_rate"]]],
    owner="jary@redhat.com",
)

feature_service_2 = FeatureService(
    name="model_v2", features=[driver_hourly_stats_view, driver_daily_miles_view], owner="jary@redhat.com",
)
