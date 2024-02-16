import requests
import json


feature_server_url = 'http://feast-feast-demo.apps.<>'

online_request = {
    "features": [
        "driver_hourly_stats:conv_rate",
    ],
    "entities": {"driver_id": [1001, 1002]},
}
r = requests.post(feature_server_url+'/get-online-features', data=json.dumps(online_request))
print(json.dumps(r.json(), indent=4, sort_keys=True))


