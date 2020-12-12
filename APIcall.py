import requests
import json

auth_data = {
    "grant_type"    : "client_credentials",
    "client_id"     : "nikicollette",
    "client_secret" : "YOUR_CLIENT_SECRET",
    "scope"         : "read_product_data"
}

# create session instance
session = requests.Session()

auth_request = session.post("https://idfs.gs.com/as/token.oauth2", data = auth_data)
access_token_dict = json.loads(auth_request.text)
access_token = access_token_dict["access_token"]

# update session headers with access token
session.headers.update({"Authorization":"Bearer "+ access_token})

request_url = "https://api.marquee.gs.com/v1/data/USCANFPP_MINI/query"

request_query = {
                    "where": {
                        "gsid": ["string1","string2","string3"]
                    },
                    "startDate": "2012-01-01",
                    "limit": 50
               }

request = session.post(url=request_url, json=request_query)
results = json.loads(request.text)
