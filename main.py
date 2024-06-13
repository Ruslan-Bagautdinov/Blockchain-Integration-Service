from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from tether_api import tether_api
from tronscan_api import tronscan_api


app = FastAPI()
app.include_router(tether_api)
app.include_router(tronscan_api)


@app.get("/")
async def root():
    return RedirectResponse(url='/docs')
