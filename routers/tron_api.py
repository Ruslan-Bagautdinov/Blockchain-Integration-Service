from fastapi import HTTPException, APIRouter
from fastapi.responses import JSONResponse, StreamingResponse

import datetime
import requests

from schemas.schemas import TransactionsQuery


tron_api = APIRouter(prefix='/tron_api', tags=['tron_api'])


@tron_api.post("/transactions/")
async def get_transactions(item: TransactionsQuery):
    """
    Fetch the last transactions of a Tron wallet
    """

    TRONGRID_API_URL = 'https://api.trongrid.io/v1'     # Can be changed anytime by Trongrid API !

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

        url = f"{TRONGRID_API_URL}/accounts/{to_wallet}/transactions/trc20"

        params = {
            'only_confirmed': only_confirmed,
            'limit': limit,
            'min_timestamp': int(date_start_dt.timestamp() * 1000),  # Convert to milliseconds
            'max_timestamp': int(date_end_dt.timestamp() * 1000)  # Convert to milliseconds
        }

        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an HTTPError if the HTTP request returned an unsuccessful status code
        response_data = response.json().get('data', [])

        amount_int = float(amount)

        for transaction in response_data:

            transaction_id = transaction.get('transaction_id', '')

            contract_data = transaction.get('token_info', {})

            currency = contract_data.get('symbol', '')

            decimals = contract_data.get('decimals', 6)

            value = transaction.get('value', '0')

            value = float(value) / 10 ** int(decimals)

            from_address = transaction.get('from', '')
            to_address = transaction.get('to', '')

            if (from_wallet is None or from_address == from_wallet) and to_address == to_wallet and value == amount_int:
                return JSONResponse(status_code=200,
                                    content={"answer": True,
                                             "transaction_id": transaction_id,
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
        raise HTTPException(status_code=500, detail="Error Connecting to Trongrid API")
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="Timeout while connecting to Trongrid API")
    except requests.exceptions.RequestException:
        raise HTTPException(status_code=500, detail="An error occurred while connecting to Trongrid API")

