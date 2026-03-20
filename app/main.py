from fastapi import FastAPI
from app.api.v1 import routes

app = FastAPI(title="PyJWT Template")
app.include_router(routes.router, prefix ="/api/v1")