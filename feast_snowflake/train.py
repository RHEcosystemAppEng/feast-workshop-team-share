from feast import FeatureStore
from datetime import datetime, timedelta
import pandas as pd
from datetime import datetime
from joblib import dump
from sklearn.linear_model import LinearRegression

orders = pd.read_csv("driver_orders.csv", sep="\t")
orders["event_timestamp"] = pd.to_datetime(orders["event_timestamp"])


entity_df = pd.DataFrame(
    {
        "event_timestamp": [
            pd.Timestamp(dt, unit="ms", tz="UTC").round("ms")
            for dt in pd.date_range(
                start=datetime.now() - timedelta(days=3),
                end=datetime.now(),
                periods=3,
            )
        ],
        "driver_id": [1001, 1002, 1003],
    }
)

store = FeatureStore(repo_path="./feature_repo")
features = ["driver_hourly_stats:conv_rate", "driver_hourly_stats:acc_rate",  "driver_hourly_stats:avg_daily_trips"]
training_df = store.get_historical_features(
    entity_df=orders,
    features=features
).to_df()

print("----- Feature schema -----\n")
print(training_df.info())

print()
print("-----  Features -----\n")
print(training_df.head())


print('------training_df----')

print(training_df)

# Train model
target = "trip_completed"

reg = LinearRegression()
train_X = training_df[training_df.columns.drop(target).drop("event_timestamp")]
train_Y = training_df.loc[:, target]
reg.fit(train_X[sorted(train_X)], train_Y)

# Save model
dump(reg, "driver_model.bin")


print()
print("-----  Materialize the latest feature values into our online store -----\n")
print(training_df.head())

store.materialize_incremental(end_date=datetime.now())

