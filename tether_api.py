import base64
import hashlib
import hmac
import json
import time
import urllib.parse
import requests
from fastapi import HTTPException, APIRouter

from config import TETHER_API_KEY, TETHER_API_SECRET

tether_api = APIRouter()

base_uri = 'https://app.tether.to/api/v1'


def md5_base64digest(string):
    if isinstance(string, str):
        string = string.encode('utf-8')
    return base64.b64encode(hashlib.md5(string).digest()).decode('utf-8')


def hmac_signature(canonical_string, api_secret):
    if isinstance(canonical_string, str):
        canonical_string = canonical_string.encode('utf-8')
    if isinstance(api_secret, str):
        api_secret = api_secret.encode('utf-8')
    return base64.b64encode(hmac.new(api_secret, canonical_string, hashlib.sha1).digest()).decode('utf-8')


def do_request(verb, uri, options=None):
    if options is None:
        options = {}

    path = base_uri + uri
    if verb in ['get', 'delete']:
        content_md5 = md5_base64digest('')
    else:
        body = json.dumps(options)
        content_md5 = md5_base64digest(body)

    headers = {
        'Content-MD5': content_md5,
        'Date': time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime()),
        'Content-Type': 'application/json',
    }
    canonical_string = (',').join([verb.upper(),
                                   headers['Content-Type'],
                                   headers['Content-MD5'],
                                   urllib.parse.urlparse(base_uri + uri).path,
                                   headers['Date']
                                   ])
    signature = hmac_signature(canonical_string, TETHER_API_SECRET)
    headers['Authorization'] = "APIAuth " + TETHER_API_KEY + ":" + signature

    if verb.lower() == 'get':
        response = requests.get(path, headers=headers)
    elif verb.lower() == 'delete':
        response = requests.delete(path, headers=headers)
    else:
        response = requests.post(path, headers=headers, data=body)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)

    return response.json()


@tether_api.get("/tether/balances")
async def get_balances():
    """
    Check the balance of a Tether wallet
    """
    return do_request('get', '/balances.json')


@tether_api.get("/tether/transactions")
async def get_transactions():
    """
    Fetch the last transactions of a Tether wallet
    """
    return do_request('get', '/transactions.json')


@tether_api.get("/tether/transactions/page/{page}")
async def get_transaction_page(page: int):
    """
    Returns a specific page of transactions
    """
    return do_request('get', f"/transactions/page/{page}.json")


@tether_api.get("/tether/transactions/{transaction_id}")
async def get_transaction_by_id(transaction_id: int):
    """
    Returns details of a specific transaction
    """
    return do_request('get', f"/transactions/{transaction_id}.json")
