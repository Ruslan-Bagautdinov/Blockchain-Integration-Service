from fastapi import HTTPException, APIRouter
import requests

from config import TRONSCAN_API_KEY, WALLET_ADDRESS

# Tronscan API base URL
TRONSCAN_API_URL = 'https://apilist.tronscan.org/api'

tronscan_api = APIRouter()


@tronscan_api.get("/tronscan/balance/{wallet_address}")
async def get_balance(wallet_address: str):
    """
    Check the balance of a Tether wallet
    """
    try:
        # Construct the URL for the Tronscan API to get the account balance
        url = f"{TRONSCAN_API_URL}/account?address={wallet_address}"
        headers = {
            'Accept': 'application/json',
            'TRON-PRO-API-KEY': TRONSCAN_API_KEY
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        # Assuming the balance is in the 'balance' field of the response
        balance = data.get('balance', 0)
        return {"balance": balance}
    except requests.exceptions.HTTPError as errh:
        raise HTTPException(status_code=404, detail="Invalid wallet address or API error")
    except requests.exceptions.ConnectionError as errc:
        raise HTTPException(status_code=500, detail="Error Connecting to Tronscan API")
    except requests.exceptions.Timeout as errt:
        raise HTTPException(status_code=504, detail="Timeout while connecting to Tronscan API")
    except requests.exceptions.RequestException as err:
        raise HTTPException(status_code=500, detail="An error occurred while connecting to Tronscan API")


@tronscan_api.get("/tronscan/transactions/{wallet_address}")
async def get_transactions(wallet_address: str):
    """
    Fetch the last transactions of a Tether wallet
    """
    try:
        # Construct the URL for the Tronscan API to get the transaction list
        url = f"{TRONSCAN_API_URL}/transaction?sort=-timestamp&count=true&limit=20&start=0&address={wallet_address}"
        headers = {
            'Accept': 'application/json',
            'TRON-PRO-API-KEY': TRONSCAN_API_KEY
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        # Assuming the transactions are in the 'data' field of the response
        transactions = data.get('data', [])
        return {"transactions": transactions}
    except requests.exceptions.HTTPError as errh:
        raise HTTPException(status_code=404, detail="Invalid wallet address or API error")
    except requests.exceptions.ConnectionError as errc:
        raise HTTPException(status_code=500, detail="Error Connecting to Tronscan API")
    except requests.exceptions.Timeout as errt:
        raise HTTPException(status_code=504, detail="Timeout while connecting to Tronscan API")
    except requests.exceptions.RequestException as err:
        raise HTTPException(status_code=500, detail="An error occurred while connecting to Tronscan API")
