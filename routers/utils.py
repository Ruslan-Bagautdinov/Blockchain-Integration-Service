import io
import qrcode
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from schemas.schemas import QRcodeQuery

utils = APIRouter(prefix='/utils', tags=['utils'])


@utils.post("/qr_code/")
async def generate_trc20_qr_code(item: QRcodeQuery):
    """
    Generate a QR code for a TRC20 wallet address.

    Args:
        item (QRcodeQuery): Query parameters including the wallet address.

    Returns:
        StreamingResponse: A streaming response containing the QR code image.
    """
    tron_wallet_address = item.wallet

    payload = f"{tron_wallet_address}"

    qr = qrcode.main.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(payload)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="transparent")

    buffer = io.BytesIO()
    img.save(buffer)
    buffer.seek(0)

    return StreamingResponse(buffer, media_type="image/png")
