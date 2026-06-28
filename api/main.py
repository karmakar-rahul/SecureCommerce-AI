from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes.dashboard import router as dashboard_router

app = FastAPI(
    title="SecureCommerce-AI API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    dashboard_router,
    prefix="/api",
    tags=["Dashboard"]
)

@app.get("/")
def home():
    return {
        "message": "SecureCommerce-AI Backend Running"
    }