import requests
import pytest
from dotenv import load_dotenv
import os

load_dotenv()
from IMAPI.user.views import get_token
from IMAPI.extensions import session

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
token_url = os.getenv("AUTH_URL")
im_customer_number = os.getenv("IM_CUSTOMER_NUMBER")
im_sender_id = os.getenv("IM_SENDERID") #
im_country_code = os.getenv("IM_COUNTRY_CODE")
im_correlation_id = os.getenv("IM_CORRELATION_ID")
im_access_token = get_token()

def test_api_request():
    url = "https://api.ingrammicro.com:443/sandbox/resellers/v6/catalog"
    params = {
        'pageNumber': 1,
        'pageSize': 25,
        'hasDiscounts': 'true',
        'category': 'Accessories',
        'skipAuthorisation': 'true',
        'groupName': 'NCE Microsoft 365 (Commercial)',
        'planName': 'Microsoft Defender for Endpoint P2 (NCE COM MTH)',
        'planId': 471490,
        'showGroupInfo': 'true'
    }
    headers = {
        'IM-CustomerNumber': os.getenv("IM_CUSTOMER_NUMBER"),
        'IM-SenderID': os.getenv("IM_SENDERID"),
        'IM-CorrelationID': os.getenv("IM_CORRELATION_ID"),
        'IM-CountryCode': 'FR',
        'Accept': 'application/json',
        'Authorization': 'Bearer '+im_access_token
    }

    response = requests.get(url, headers=headers, params=params)
    assert response.status_code == 200
    data = response.json()
    assert 'catalog' in data

if __name__ == "__main__":
    pytest.main()
