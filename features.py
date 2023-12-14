from datetime import timedelta

import pandas as pd
from feast import (
    FeatureView,
    Field,
)
from feast.types import (
    Float32,
    Float64,
    UnixTimestamp
)

from data_sources import *
from entities import *

driver_hourly_stats_view = FeatureView(
    name="driver_hourly_stats",
    description="Hourly features",
    entities=[driver],
    ttl=timedelta(seconds=8640000000),
    schema=[
        Field(name="conv_rate", dtype=Float32),
        Field(name="acc_rate", dtype=Float32),
    ],
    online=True,
    source=driver_stats,
    tags={"production": "True"},
    owner="test2@gmail.com",
)

driver_daily_miles_view = FeatureView(
    name="driver_daily_miles",
    description="Daily miles",
    entities=[driver],
    ttl=timedelta(seconds=8640000000),
    schema=[
        Field(name="day", dtype=UnixTimestamp),
        Field(name="miles_driven", dtype=Float64),
    ],
    online=True,
    source=driver_stats,
    tags={"production": "True"},
    owner="jary@redhat.com",
)
