from fastapi import HTTPException, APIRouter
from fastapi.responses import JSONResponse, StreamingResponse, FileResponse
from pydantic import BaseModel, field_validator
from typing import Optional

import datetime
import requests

import qrcode
import io

tron_api = APIRouter(prefix='/tron_api', tags=['tron_api'])


class TransactionsQuery(BaseModel):

    wallet: str
    own_wallet: str
    amount: str
    date_start: Optional[str] = None
    date_end: Optional[str] = None
    limit: Optional[int] = 20
    only_confirmed: Optional[bool] = True

    @field_validator('amount')
    def validate_amount(cls, value):
        try:
            float(value)
        except ValueError:
            raise ValueError("Amount must be a valid number")
        return value

    @field_validator('date_start', 'date_end')
    def validate_date(cls, value, field):
        if value is not None and value != "string":
            try:
                datetime.datetime.strptime(value, "%d-%m-%Y %H:%M:%S")
            except ValueError:
                raise ValueError(f"{field.name} must be in the format 'dd-mm-yyyy HH:MM:SS'")
        return value


class QRcodeQuery(BaseModel):

    wallet: str


@tron_api.post("/transactions/")
async def get_transactions(item: TransactionsQuery):
    """
    Fetch the last transactions of a Tron wallet
    """

    TRONGRID_API_URL = 'https://api.trongrid.io/v1'     # Can be changed anytime by Trongrid API !


    wallet = item.wallet
    own_wallet = item.own_wallet
    amount = item.amount
    date_start = item.date_start
    date_end = item.date_end
    limit = item.limit
    only_confirmed = item.only_confirmed

    try:
        # Set default values for date_start and date_end if not provided
        now = datetime.datetime.now()

        if date_start is None or date_start == "string":
            date_start_dt = now - datetime.timedelta(hours=6)  # 6 hours ago
        else:
            date_start_dt = datetime.datetime.strptime(date_start, "%d-%m-%Y %H:%M:%S")

        if date_end is None or date_end == "string":
            date_end_dt = now
        else:
            date_end_dt = datetime.datetime.strptime(date_end, "%d-%m-%Y %H:%M:%S")

        url = f"{TRONGRID_API_URL}/accounts/{wallet}/transactions/trc20"

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

            contract_data = transaction.get('token_info', {})

            currency = contract_data.get('symbol', '')

            decimals = contract_data.get('decimals', 6)

            value = transaction.get('value', '0')

            value = float(value) / 10 ** int(decimals)

            from_address = transaction.get('from', '')
            to_address = transaction.get('to', '')

            if from_address == wallet and to_address == own_wallet and value == amount_int:
                return JSONResponse(status_code=200, content={"answer": True})

        return JSONResponse(status_code=200, content={"answer": False})

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


@tron_api.post("/qr_code/")
async def generate_trc20_qr_code(item: QRcodeQuery):

    tron_wallet_address = item.wallet

    payload = f"{tron_wallet_address}"

    # Generate the QR code
    qr = qrcode.main.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(payload)
    qr.make(fit=True)

    # Create an image from the QR code instance with a transparent background
    img = qr.make_image(fill_color="black", back_color="transparent")

    buffer = io.BytesIO()
    img.save(buffer)
    buffer.seek(0)

    return StreamingResponse(buffer, media_type="image/png")
