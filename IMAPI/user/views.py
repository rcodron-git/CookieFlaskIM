# -*- coding: utf-8 -*-
"""User views."""
from flask import Blueprint, render_template
from flask_login import login_required
import requests
from dotenv import load_dotenv
import os
load_dotenv()  # take environment variables from .env.
import certifi
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
token_url = os.getenv("AUTH_URL")

blueprint = Blueprint("user", __name__, url_prefix="/users", static_folder="../static")
ca_bundle_path = certifi.where()  # Use certifi's CA bundle

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
    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials'
    }
    response = requests.post(token_url, data=data)
    response = requests.post(token_url, data=payload, verify=ca_bundle_path)
    response.raise_for_status()

    token_info = response.json()
    print("-------------------")
    print("TOKEN INFO")
    print(token_info)
    print("-------------------")
    return response.json()