import json
import base64
import requests

from config import *

if PAYPAL_MODE == 'sandbox':
    PAYPAL_BASE_URL = "https://api.sandbox.paypal.com"
else:
    PAYPAL_BASE_URL = "https://api.paypal.com"

def get_token():
    client_id = PAYPAL_CLIENT_ID
    client_secret = PAYPAL_CLIENT_SECRET

    credentials = "%s:%s" % (client_id, client_secret)
    encode_credential = base64.b64encode(credentials.encode('utf-8')).decode('utf-8').replace("\n", "")

    headers = {
        "Authorization": ("Basic %s" % encode_credential),
        'Accept': 'application/json',
        'Accept-Language': 'en_US',
    }
    param = {'grant_type': 'client_credentials'}


    url = '{}/v1/oauth2/token'.format(PAYPAL_BASE_URL)
    r = requests.post(url, headers=headers, data=param)
    response = json.loads(r.text)
    return response['access_token']


def create_product(name, description, type='SERVICE', category='SOFTWARE', image_url='', home_url=''):
    """
    Reference: https://developer.paypal.com/docs/api/catalog-products/v1/
    :param name: Product name
    :param description: product description
    :param type: PHYSICAL/DIGITAL/SERVICE, default = PHYSICAL
    :param category:
    :param image_url: The image URL for the product. length = 1~2000
    :param home_url: The home page URL for the product. length = 1~2000
    :return:
    """
    created_product = None

    token = get_token()
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
    }

    url = '{}/v1/catalogs/products'.format(PAYPAL_BASE_URL)
    data = {
        "name": name,
        "description": description,
        "type": type,
        "category": category,
        # "image_url": image_url,
        # "home_url": home_url
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code == 201:
        created_product = json.loads(response.text)
        print(created_product)

    return created_product


def create_plan(product_id, name, description, frequency='MONTH', total_cycles='0', price='9.99', currency='USD',
                setup_fee="0", setup_currency="USD", tax_percentage="0"):
    """

    :param product_id:
    :param name:
    :param description:
    :param frequency:
    :param total_cycles:
    :param price:
    :param currency:
    :param setup_fee:
    :param setup_currency:
    :param tax_percentage:
    :return:
    """

    created_plan = None

    token = get_token()
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
    }

    url = '{}/v1/billing/plans'.format(PAYPAL_BASE_URL)
    data = {
        "product_id": product_id,
        "name": name,
        "description": description,
        "status": "ACTIVE",
        "billing_cycles": [

            {
                "frequency": {
                    "interval_unit": frequency,
                    "interval_count": 1
                },
                "tenure_type": "REGULAR",
                "sequence": 1,
                "total_cycles": total_cycles,
                "pricing_scheme": {
                    "fixed_price": {
                        "value": price,
                        "currency_code": currency
                    }
                }
            }
        ],
        "payment_preferences": {
            "auto_bill_outstanding": "true",
            "setup_fee": {
                "value": setup_fee,
                "currency_code": setup_currency
            },
            "setup_fee_failure_action": "CONTINUE",
            "payment_failure_threshold": 3
        },
        "taxes": {
            "percentage": tax_percentage,
            "inclusive": "false"
        }
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code == 201:
        created_plan = json.loads(response.text)
        print(created_plan)

    return created_plan

def get_plans():
    plans = []
    token = get_token()
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
    }

    url = '{}/v1/billing/plans'.format(PAYPAL_BASE_URL)
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        plans = json.loads(response.text)['plans']

    return plans

def get_subscribe_details(subscribe_id):
    subscribe_details = None
    token = get_token()
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
    }

    url = '{}/v1/billing/subscriptions/{}'.format(PAYPAL_BASE_URL ,subscribe_id)
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        subscribe_details = json.loads(response.text)

    return subscribe_details

def unsubscribe(subscription_id):
    success = False
    token = get_token()
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
    }

    url = '{}/v1/billing/subscriptions/{}/suspend'.format(PAYPAL_BASE_URL, subscription_id)
    data = {
        "reason": "Not satisfied with the service"
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    print(response.text)
    if response.status_code == 204:
        success = True

    return success


def resubscribe(subscription_id):
    success = False
    token = get_token()
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
    }

    url = '{}/v1/billing/subscriptions/{}/activate'.format(PAYPAL_BASE_URL, subscription_id)
    data = {
        "reason": "Reactivating the subscription"
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    print(response.text)
    if response.status_code == 204:
        success = True

    return success
