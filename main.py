from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

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
