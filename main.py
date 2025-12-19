from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import subprocess
import uuid
import os

app = FastAPI()

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

@app.post("/descargar")
def descargar_video(data: Link):
    # Validación básica
    if not data.url.startswith("http"):
        return JSONResponse(
            status_code=400,
            content={"error": "URL inválida"},
        )

    video_id = str(uuid.uuid4())
    output_file = f"{video_id}.mp4"

    command = [
        "yt-dlp",
        "-f",
        "bv*[vcodec=avc1]/bv*",
        "--merge-output-format",
        "mp4",
        "-o",
        output_file,
        data.url,
    ]

    try:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=60,
        )

        # Si yt-dlp falla
        if result.returncode != 0 or not os.path.exists(output_file):
            return JSONResponse(
                status_code=400,
                content={"error": "No se pudo descargar este video"},
            )

        return FileResponse(
            path=output_file,
            filename="video.mp4",
            media_type="video/mp4",
        )

    except Exception:
        return JSONResponse(
            status_code=500,
            content={"error": "Error interno del servidor"},
        )
