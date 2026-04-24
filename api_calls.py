import requests
import json

def call_api(url, query):
    try:
        response = requests.get(url.format(query=query), timeout=10)
        if response.status_code == 200:
            data = response.json()
            return json.dumps(data, indent=2)
        return f"API Error: {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"

def tg_to_number(query):
    from config import API_TG_TO_NUMBER
    return call_api(API_TG_TO_NUMBER, query)

def gst_lookup(query):
    from config import API_GST
    return call_api(API_GST, query)

def vehicle_lookup(query):
    from config import API_VEHICLE
    return call_api(API_VEHICLE, query)

def ifsc_lookup(query):
    from config import API_IFSC
    return call_api(API_IFSC, query)
