import requests
import json
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth
import os
from dotenv import load_dotenv

load_dotenv()


# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))
def get_request(url, **kwargs):
    print(kwargs)
    print("GET from {} ".format(url))
    try:
        # Call get method of requests library with URL and parameters
        response = requests.get(url, headers={'Content-Type': 'application/json'},
                                    params=kwargs)
    except:
        # If any error occurs
        print("Network exception occurred")
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data


# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)
def post_request(url, json_payload, **kwargs):
    print("Payload: ", json_payload, ". Params: ", kwargs)
    print(f"POST {url}")
    try:
        response = requests.post(url, headers={'Content-Type': 'application/json'},
                                 json=json_payload, params=kwargs)
    except:
        # If any error occurs
        print("Network exception occurred")
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data


# Create a get_dealers_from_cf method to get dealers from a cloud function
# def get_dealers_from_cf(url, **kwargs):
# - Call get_request() with specified arguments
# - Parse JSON results into a CarDealer object list
def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)
    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result
        # For each dealer object
        for dealer in dealers:
            # Get its content in `doc` object
            dealer_doc = dealer["doc"]
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                                   id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"],
                                   st=dealer_doc["st"], zip=dealer_doc["zip"])
            results.append(dealer_obj)

    return results

# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
# def get_dealer_by_id_from_cf(url, dealerId):
# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list
def get_dealer_by_id_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url, dealerId=kwargs['dealer_id'])
    if json_result:
        for review in json_result:
            # Get its content in `doc` object
            review_doc = review["doc"]
        # Create a Review object with values in `doc` object
            if review_doc['purchase']:
                review_obj = DealerReview(
                    dealership=review_doc["dealership"],
                    name=review_doc["name"],
                    purchase=review_doc["purchase"],
                    review=review_doc["review"],
                    purchase_date=review_doc["purchase_date"],
                    car_make=review_doc["car_make"],
                    car_model=review_doc["car_model"],
                    car_year=review_doc["car_year"],
                    sentiment=analyze_review_sentiments(review_doc["review"]),
                    id=review_doc["id"],
                )
            else:
                review_obj = DealerReview(
                    dealership=review_doc["dealership"],
                    name=review_doc["name"],
                    purchase=review_doc["purchase"],
                    review=review_doc["review"],
                    purchase_date="N/A",
                    car_make="N/A",
                    car_model="N/A",
                    car_year="N/A",
                    sentiment=analyze_review_sentiments(review_doc["review"]),
                    id=review_doc["id"],
                )
            results.append(review_obj)
    return results

# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative
def analyze_review_sentiments(text):
    URL = 'https://api.us-south.natural-language-understanding.watson.cloud.ibm.com/instances/90cf5cad-ad7a-4718-8dcb-23bb2d445cd9/v1/analyze?version=2019-07-12'
    API_KEY = os.getenv('NLU_API_KEY')
    params = json.dumps({"text": text, "features": {"sentiment": {}}})
    response = requests.post(
        URL, data=params, headers={'Content-Type': 'application/json'}, auth=HTTPBasicAuth('apikey', API_KEY)
    )
    print(response)
    try:
        return response.json()['sentiment']['document']['label']
    except KeyError:
        return 'neutral'


