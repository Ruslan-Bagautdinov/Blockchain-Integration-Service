from fastapi import FastAPI, HTTPException, APIRouter
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field, field_validator
from typing import Optional

import datetime
import requests

from schemas.schemas import TransactionsQuery
from config import ETHERSCAN_API_KEY

app = FastAPI()
erc20_api = APIRouter(prefix='/erc20_api', tags=['erc20_api'])


@erc20_api.post("/transactions/")
async def get_transactions(item: TransactionsQuery):
    """
    Fetch the last transactions of an ERC20 wallet
    """

    ETHERSCAN_API_URL = 'https://api.etherscan.io/api'  # Can be changed based on the Ethereum API provider

    from_wallet = item.from_wallet
    to_wallet = item.to_wallet
    amount = item.amount
    date_start = item.date_start
    date_end = item.date_end
    limit = item.limit
    only_confirmed = item.only_confirmed

    try:
        # Set default values for date_start and date_end if not provided
        now = datetime.datetime.now()

        if from_wallet == "string":
            from_wallet = None

        if date_start is None or date_start == "string":
            date_start_dt = now - datetime.timedelta(hours=6)  # 6 hours ago
        else:
            date_start_dt = datetime.datetime.strptime(date_start, "%d-%m-%Y %H:%M:%S")

        if date_end is None or date_end == "string":
            date_end_dt = now
        else:
            date_end_dt = datetime.datetime.strptime(date_end, "%d-%m-%Y %H:%M:%S")

        params = {
            'module': 'account',
            'action': 'txlist',
            'address': to_wallet,
            'startblock': 0,
            'endblock': 99999999,
            'sort': 'asc',
            'apikey': ETHERSCAN_API_KEY  # Replace with your Etherscan API key
        }

        response = requests.get(ETHERSCAN_API_URL, params=params)
        response.raise_for_status()  # Raise an HTTPError if the HTTP request returned an unsuccessful status code
        response_data = response.json().get('result', [])

        amount_int = float(amount)

        for transaction in response_data:
            value = int(transaction.get('value', '0')) / 10 ** 18  # Convert wei to ETH
            from_address = transaction.get('from', '')
            to_address = transaction.get('to', '')

            if (from_wallet is None or from_address == from_wallet) and to_address == to_wallet and value == amount_int:
                return JSONResponse(status_code=200,
                                    content={"answer": True,
                                             "transaction_id": transaction.get('hash', ''),
                                             "from_address": from_address
                                             }
                                    )

        return JSONResponse(status_code=200,
                            content={"answer": False,
                                     "transaction_id": None,
                                     "from_address": None
                                     }
                            )

    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid date format. Please use 'dd-mm-yyyy HH:MM:SS'")
    except requests.exceptions.HTTPError:
        raise HTTPException(status_code=404, detail="Invalid wallet address or API error")
    except requests.exceptions.ConnectionError:
        raise HTTPException(status_code=500, detail="Error Connecting to Etherscan API")
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="Timeout while connecting to Etherscan API")
    except requests.exceptions.RequestException:
        raise HTTPException(status_code=500, detail="An error occurred while connecting to Etherscan API")
