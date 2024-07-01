from fastapi import FastAPI
from fastapi.responses import RedirectResponse

#routers
from routers.utils import utils
from routers.tron_api import tron_api
from routers.erc20_api import erc20_api

app = FastAPI()
app.include_router(utils)
app.include_router(tron_api)
app.include_router(erc20_api)


@app.get("/")
async def root():
    return RedirectResponse(url='/docs')
