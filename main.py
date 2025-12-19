from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# PERMITIR LLAMADAS DESDE CUALQUIER WEB (por ahora)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Link(BaseModel):
    url: str

@app.get("/")
def root():
    return {"status": "backend vivo"}

@app.post("/recibir")
def recibir_link(link: Link):
    return {
        "message": f"Backend recibió el link: {link.url}"
    }
