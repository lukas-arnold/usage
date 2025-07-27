from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from app.database import init_db
from app.routers.electricity import electricity_router
from app.routers.oil import oil_router
from app.routers.water import water_router


app = FastAPI(
    title="Verbrauchsübersicht",
)

init_db()

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=FileResponse)
async def read_root_frontend():
    return FileResponse(os.path.join("static", "index.html"))


app.include_router(electricity_router)
app.include_router(oil_router)
app.include_router(water_router)
