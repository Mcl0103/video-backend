from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import subprocess
import uuid
import os
import time
def limpiar_archivos(*archivos):
    time.sleep(10)
    for archivo in archivos:
        if os.path.exists(archivo):
            os.remove(archivo)

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
def descargar_video(data: Link, background_tasks: BackgroundTasks):
    if not data.url.startswith("http"):
        return JSONResponse(
            status_code=400,
            content={"error": "URL inválida"},
        )

    uid = str(uuid.uuid4())
    raw_file = f"{uid}.mkv"
    final_file = f"{uid}.mp4"

    try:
        # 1️⃣ Descargar el video (sin importar el códec)
        subprocess.run(
            ["yt-dlp", data.url, "-o", raw_file],
            check=True,
        )

        if not os.path.exists(raw_file):
            raise Exception("No se descargó el archivo")

        # 2️⃣ Convertir SI O SI a MP4 H.264
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

        # 3️⃣ LIMPIEZA AUTOMÁTICA (después de enviar)
      background_tasks.add_task(limpiar_archivos, raw_file, final_file)

        return FileResponse(
            final_file,
            filename="video.mp4",
            media_type="video/mp4",
        )

    except Exception:
        return JSONResponse(
            status_code=500,
            content={"error": "No se pudo procesar el video"},
        )
