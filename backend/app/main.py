from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.router import api_router

app = FastAPI(title="Tramix API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://tramix.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

@app.get("/")
def read_root():
    return {"Hello": "World"}
