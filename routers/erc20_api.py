import datetime

import requests
from fastapi import HTTPException, APIRouter
from fastapi.responses import JSONResponse
from loguru import logger

from config import ETHERSCAN_API_KEY
from schemas.schemas import TransactionsQuery

erc20_api = APIRouter(prefix='/erc20_api', tags=['erc20_api'])


@erc20_api.post("/transactions/")
async def get_transactions(item: TransactionsQuery):
    """
    Fetch the last transactions of an ERC20 wallet.

    Args:
        item (TransactionsQuery): Query parameters including wallet addresses, amount, date range, and limit.

    Returns:
        JSONResponse: A JSON response containing the transaction details if found.
    """
    ETHERSCAN_API_URL = 'https://api.etherscan.io/api'

    from_wallet = item.from_wallet
    to_wallet = item.to_wallet
    amount = item.amount
    date_start = item.date_start
    date_end = item.date_end
    limit = item.limit
    only_confirmed = item.only_confirmed

    try:
        now = datetime.datetime.now()

        if from_wallet == "string":
            from_wallet = None

        date_start_dt = now - datetime.timedelta(
            hours=6) if date_start is None or date_start == "string" else datetime.datetime.strptime(date_start,
                                                                                                     "%d-%m-%Y %H:%M:%S")
        date_end_dt = now if date_end is None or date_end == "string" else datetime.datetime.strptime(date_end,
                                                                                                      "%d-%m-%Y %H:%M:%S")

        params = {
            'module': 'account',
            'action': 'txlist',
            'address': to_wallet,
            'startblock': 0,
            'endblock': 99999999,
            'sort': 'asc',
            'apikey': ETHERSCAN_API_KEY
        }

        response = requests.get(ETHERSCAN_API_URL, params=params)
        response.raise_for_status()
        response_data = response.json().get('result', [])

        amount_int = float(amount)

        for transaction in response_data:
            value = int(transaction.get('value', '0')) / 10 ** 18
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
        logger.error(f"Invalid date format: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid date format. Please use 'dd-mm-yyyy HH:MM:SS'")
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTPError: {str(e)}")
        raise HTTPException(status_code=404, detail="Invalid wallet address or API error")
    except requests.exceptions.ConnectionError as e:
        logger.error(f"ConnectionError: {str(e)}")
        raise HTTPException(status_code=500, detail="Error Connecting to Etherscan API")
    except requests.exceptions.Timeout as e:
        logger.error(f"Timeout: {str(e)}")
        raise HTTPException(status_code=504, detail="Timeout while connecting to Etherscan API")
    except requests.exceptions.RequestException as e:
        logger.error(f"RequestException: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred while connecting to Etherscan API")
