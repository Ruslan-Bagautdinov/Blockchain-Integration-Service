from fastapi import FastAPI
from fastapi.responses import RedirectResponse

#own import
from tron_api import tron_api


app = FastAPI()
app.include_router(tron_api)


@app.get("/")
async def root():
    return RedirectResponse(url='/docs')
