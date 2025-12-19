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
    if not data.url.startswith("http"):
        return JSONResponse(status_code=400, content={"error": "URL inválida"})

    uid = str(uuid.uuid4())
    raw_file = f"{uid}.mkv"
    final_file = f"{uid}.mp4"

    try:
        # 1️⃣ Descargar SIN importar el códec
        subprocess.run(
            [
                "yt-dlp",
                data.url,
                "-o",
                raw_file,
            ],
            check=True,
        )

        if not os.path.exists(raw_file):
            raise Exception("No se descargó el archivo")

        # 2️⃣ Convertir SI O SI a H.264
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                raw_file,
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p",
                "-movflags",
                "+faststart",
                final_file,
            ],
            check=True,
        )

        if not os.path.exists(final_file):
            raise Exception("No se creó el MP4")

        return FileResponse(
            final_file,
            filename="video.mp4",
            media_type="video/mp4",
        )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": "No se pudo procesar el video"},
        )
