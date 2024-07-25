from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from routers.erc20_api import erc20_api
from routers.tron_api import tron_api
# Routers
from routers.utils import utils

app = FastAPI(
    title="Blockchain Integration Service",
    description="""
    A FastAPI service to integrate blockchain functionalities such as Tron and ERC20 transactions, 
    and utility tools like QR code generation.
    """,
    version="1.0.0"
)

app.include_router(utils)
app.include_router(tron_api)
app.include_router(erc20_api)


@app.get("/")
async def root():
    """
    Redirect to the API documentation.
    """
    return RedirectResponse(url='/docs')
