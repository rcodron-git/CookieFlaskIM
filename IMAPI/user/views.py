# -*- coding: utf-8 -*-
"""User views."""
#from datetime import time
import time

from blib2to3.pytree import convert
from flask import Blueprint, render_template
from flask_login import login_required
import requests
from dotenv import load_dotenv
import os
load_dotenv()  # take environment variables from .env.
import certifi
from flask import session, request
#Need to import the models Catalog
from IMAPI.user.models import Catalog
from IMAPI.extensions import db


client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
token_url = os.getenv("AUTH_URL")
blueprint = Blueprint("user", __name__, url_prefix="/users", static_folder="../static")
ca_bundle_path = certifi.where()  # Use certifi's CA bundle
im_customer_number = os.getenv("IM_CUSTOMER_NUMBER")
im_sender_id = os.getenv("IM_SENDERID") #
im_country_code = os.getenv("IM_COUNTRY_CODE")

def generate_request_id():
    """Generate a unique request ID."""
    import uuid

    return str(uuid.uuid4())

def check_correlation_id():
    # check if the correlation id is in the session
    if session.get('correlation_id') is None:
        # if not, generate a new one
        session['correlation_id'] = generate_request_id()
    return session['correlation_id']

def create_new_correlation_id():
    session['correlation_id'] = generate_request_id()
    return session['correlation_id']

def get_token():
    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials'
    }
    response = requests.post(token_url, data=data)
    response = requests.post(token_url, data=payload, verify=ca_bundle_path)
    response.raise_for_status()

    token_info = response.json()

    # save the token in the session
    session['token'] = token_info['access_token']
    # calculate the time when the token will expire
    session['expires_at'] = str(time.time() + float(token_info['expires_in']))
    session['token_type'] = token_info['token_type']
    return session['token']


def token_still_valid():
    if session.get('expires_at') is None:
        return False
    if session.get('token') is None:
        return False
    if time.time() > float(session['expires_at']):
        return False
    if time.time() < float(session['expires_at']):
        return True

def create_headers(token):
    headers = {
        'IM-CustomerNumber': im_customer_number,
        'IM-SenderID': im_sender_id,
        'IM-CountryCode': "FR",
        'IM-CorrelationID': check_correlation_id(),
        'Accept-Language': 'en',
        'Accept': 'application / json',
        'Authorization': f'Bearer {token}'
    }
    print(headers)
    return headers

@blueprint.route("/")
@login_required
def members():
    """List members."""
    return render_template("users/members.html")

# Define the payload for the POST request
payload = {
    'grant_type': 'client_credentials',
    'client_id': client_id,
    'client_secret': client_secret
}

#let's a view to get the token
@blueprint.route("/token")
def token():
    if token_still_valid() is False:
        token = get_token()
    else:
        token = session['token']
    return token

@blueprint.route("/search_product")
def search_product():
    # Vérifier si aucun paramètre n'est fourni
    if not request.args:
        return render_template("users/catalog/search_catalog.html", catalog=[])

    # Définir les paramètres par défaut
    params = {
        'pageSize': request.args.get('pageSize', 25),
        'type': request.args.get('type', 'IM::any'),
        'hasDiscounts': 'true' if request.args.get('hasDiscounts') == 'Yes' else 'false',
        'vendor': request.args.getlist('vendor'),
        'vendorPartNumber': request.args.getlist('vendorPartNumber'),
        'vendorNumber': request.args.get('vendorNumber'),
        'keyword': request.args.getlist('keyword'),
        'category': request.args.get('category'),
        'skipAuthorisation': 'true' if request.args.get('skipAuthorisation') == 'Yes' else 'false',
        'groupName': request.args.get('groupName'),
        'planName': request.args.get('planName'),
        'planId': request.args.get('planId'),
        'showGroupInfo': 'true' if request.args.get('showGroupInfo') == 'Yes' else 'false'
    }

    # Filtrer les paramètres pour ne conserver que ceux qui sont fournis et non vides
    params = {k: v for k, v in params.items() if v and v != 'false'}

    # Obtenir le token
    token = None
    if not token_still_valid():
        token = get_token()
    else:
        token = session['token']

    # Définir les en-têtes
    headers = {
        'IM-CustomerNumber': os.getenv("IM_CUSTOMER_NUMBER"),
        'IM-SenderID': os.getenv("IM_SENDERID"),
        'IM-CorrelationID': check_correlation_id(),
        'IM-CountryCode': 'FR',
        'Accept': 'application/json',
        'Authorization': f'Bearer {token}',
    }

    # Faire une requête à l'endpoint du catalogue
    url = os.getenv('URL_BASE') + "resellers/v6/catalog"
    response = requests.get(url, headers=headers, params=params)
    print(url)
    print(params)
    response.raise_for_status()

    # Retourner la réponse JSON
    catalog = response.json().get('catalog', [])

    # Rendre la page HTML avec les résultats de la recherche
    return render_template("users/catalog/search_catalog.html", catalog=catalog)

def str_to_bool(value):
    return value.lower() in ('true', '1', 't', 'y', 'yes')
"""
@blueprint.route("/save_catalog")
def save_catalog():
    token = None
    if token_still_valid() is False:
        token = get_token()
    else:
        token = session['token']
    headers = {
        'IM-CustomerNumber': os.getenv("IM_CUSTOMER_NUMBER"),
        'IM-SenderID': os.getenv("IM_SENDERID"),
        'IM-CorrelationID': 'fbac82ba-cf0a-4bcf',
        'IM-CountryCode': 'FR',
        'Accept': 'application/json',
        'Authorization': f'Bearer {token}',
    }
    url = os.getenv('URL_BASE')+"resellers/v6/catalog"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    if response.status_code != 200:
        return response.json()
    catalog = response.json()

    for item in catalog.get('catalog', []):
        catalog_item = Catalog(
            description=item.get('description', ''),
            category=item.get('category', ''),
            subCategory=item.get('subCategory', ''),
            productType=item.get('productType', ''),
            ingramPartNumber=item.get('ingramPartNumber', ''),
            vendorPartNumber=item.get('vendorPartNumber', ''),
            upcCode=item.get('upcCode', ''),
            vendorName=item.get('vendorName', ''),
            endUserRequired=str_to_bool(item.get('endUserRequired', 'False')),
            hasDiscounts=str_to_bool(item.get('hasDiscounts', 'False')),
            sku_type=item.get('type', ''),
            discontinued=str_to_bool(item.get('discontinued', 'False')),
            newProduct=str_to_bool(item.get('newProduct', 'False')),
            directShip=str_to_bool(item.get('directShip', 'False')),
            hasWarranty=str_to_bool(item.get('hasWarranty', 'False')),
            extraDescription=item.get('extraDescription', ''),
            replacementSku=item.get('replacementSku', ''),
            authorizedToPurchase=str_to_bool(item.get('authorizedToPurchase', 'True'))
        )

        db.session.add(catalog_item)
        db.session.commit()
        # now I want to iterate on each page to get all the data
        # the next page is in response.json() like  'nextPage': '/resellers/v6/catalog?pageSize=25&pageNumber=2&showGroupInfo=False'}
        # so we can get the next page by doing response.json()['nextPage']
        try:
            while response.json().get('nextPage') is not None:
                response = requests.get(os.getenv('URL_BASE') + "" + response.json()['nextPage'],
                                        headers=headers)
                response.raise_for_status()
                for item in catalog.get('catalog', []):
                    catalog_item = Catalog(
                        description=item.get('description', ''),
                        category=item.get('category', ''),
                        subCategory=item.get('subCategory', ''),
                        productType=item.get('productType', ''),
                        ingramPartNumber=item.get('ingramPartNumber', ''),
                        vendorPartNumber=item.get('vendorPartNumber', ''),
                        upcCode=item.get('upcCode', ''),
                        vendorName=item.get('vendorName', ''),
                        endUserRequired=str_to_bool(item.get('endUserRequired', 'False')),
                        hasDiscounts=str_to_bool(item.get('hasDiscounts', 'False')),
                        sku_type=item.get('type', ''),
                        discontinued=str_to_bool(item.get('discontinued', 'False')),
                        newProduct=str_to_bool(item.get('newProduct', 'False')),
                        directShip=str_to_bool(item.get('directShip', 'False')),
                        hasWarranty=str_to_bool(item.get('hasWarranty', 'False')),
                        extraDescription=item.get('extraDescription', ''),
                        replacementSku=item.get('replacementSku', ''),
                        authorizedToPurchase=str_to_bool(item.get('authorizedToPurchase', 'True'))
                    )
                    db.session.add(catalog_item)
                    db.session.commit()
        except Exception as e:
            print(e)
            # convert e to json and return
            error_json = {
                'error': str(e)
            }
            return error_json

    catalog_ok = {
        'status': 'ok'
    }

    return catalog_ok
"""
#we need a view to see the catalog items from the api
@blueprint.route("/online-catalog")
def online_catalog():
    url = None
    #if we received a get request
    if request.method == "GET":
        if request.args.get('page') is not None:
            url = os.getenv("URL_BASE")+request.args.get('page')
        token = None
        if token_still_valid() is False:
            token = get_token()
        else:
            token = session['token']
        # set the headers
        headers = {
            'IM-CustomerNumber': os.getenv("IM_CUSTOMER_NUMBER"),
            'IM-SenderID': os.getenv("IM_SENDERID"),
            'IM-CorrelationID': 'fbac82ba-cf0a-4bcf',
            'IM-CountryCode': 'FR',
            'Accept': 'application/json',
            'Authorization': f'Bearer {token}',
        }
        # make a request to the catalog endpoint
        if url is None:
            url = os.getenv('URL_BASE')+"resellers/v6/catalog"
        else :
            url = os.getenv('URL_BASE') + url
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        catalog = response.json()
        return render_template("users/catalog_list.html", items=catalog.get('catalog', []), page=catalog.get('nextPage', 1), total=catalog.get('total', 0))

@blueprint.route("/online-catalog/<string:id>")
def catalog_item(id):
    # get the catalog item by id
    url = None

    if request.method == "GET":
        if id is not None:
            #https://api.ingrammicro.com:443/sandbox/resellers/v6/catalog/details/{ingramPartNumber}
            url = f"resellers/v6/catalog/details/{id}"
        token = None
        if token_still_valid() is False:
            token = get_token()
        else:
            token = session['token']
        # set the headers
        headers = {
            'IM-CustomerNumber': os.getenv("IM_CUSTOMER_NUMBER"),
            'IM-SenderID': os.getenv("IM_SENDERID"),
            'IM-CorrelationID': 'fbac82ba-cf0a-4bcf',
            'IM-CountryCode': 'FR',
            'Accept': 'application/json',
            'Authorization': f'Bearer {token}',
        }
        # make a request to the catalog endpoint
        if url is None:
            url = os.getenv('URL_BASE')+"resellers/v6/catalog"
            error_json = {
                'error': 'No ID provided'
            }
            return Exception("No ID provided")
        else :
            url = os.getenv('URL_BASE') + url
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        return render_template("users/item_detail.html", item=response.json())

@blueprint.route("/orders/search")
def orders_search():
    url = "resellers/v6/orders/search"
    token = None
    if token_still_valid() is False:
        token = get_token()
    else:
        token = session['token']
    # set the headers
    headers = {
        #'IM-CustomerNumber': os.getenv("IM_CUSTOMER_NUMBER"),
        # Change for the test
        'IM-CustomerNumber': "20-222222",

        'IM-SenderID': os.getenv("IM_SENDERID"),
        'IM-CorrelationID': 'fbac82ba-cf0a-4bcf-fc03-0c5084',
        'IM-CountryCode': 'US',
        'Accept': 'application/json',
        'Authorization': f'Bearer {token}',
    }
    # make a request to the catalog endpoint
    url = os.getenv('URL_BASE') + url
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    #print(response.json())
    return render_template("users/orders/search_orders.html", orders=response.json())

@blueprint.route("/orders/detail/<string:order_number>")
def order_detail(order_number):
    url = f"resellers/v6.1/orders/{order_number}"
    token = None
    if token_still_valid() is False:
        token = get_token()
    else:
        token = session['token']
    headers = {
        #'IM-CustomerNumber': os.getenv("IM_CUSTOMER_NUMBER"),
        'IM-CustomerNumber': "20-222222",
        #'IM-SenderID': os.getenv("IM_SENDERID"),
        'IM-SenderID': "20-222222",
        'IM-CorrelationID': 'fbac82ba-cf0a-4bcf-fc03-0c5084',
        #'IM-CountryCode': 'FR',
        'IM-CountryCode': 'US',

        'Accept': 'application/json',
        'Authorization': f'Bearer {token}',
    }
    print(headers)
    #https://api.ingrammicro.com:443/sandbox/resellers/v6.1/orders/{ordernumber}
    # https://api.ingrammicro.com/sandbox/resellers/v6/orders/20-VWMRP
    url = os.getenv('URL_BASE') + url
    url = "https://api.ingrammicro.com:443/sandbox/resellers/v6.1/orders/20-VWMRP"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    order_details = response.json()
    return render_template("users/orders/orders_detail.html", order=order_details)
