from fastapi import FastAPI, BackgroundTasks, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
import subprocess
import uuid
import os
import time

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def limpiar_archivos(*archivos):
    time.sleep(15)
    for archivo in archivos:
        if os.path.exists(archivo):
            try:
                os.remove(archivo)
            except:
                pass

@app.get("/")
def root():
    return {"status": "backend vivo"}

@app.post("/descargar")
def descargar_video(
    url: str = Form(...),
    background_tasks: BackgroundTasks = None,
):
    if not url.startswith("http"):
        return JSONResponse(
            status_code=400,
            content={"error": "URL inválida"},
        )

    uid = str(uuid.uuid4())
    raw_file = f"{uid}.mkv"
    final_file = f"{uid}.mp4"

    try:
        # 1️⃣ Descargar video
        subprocess.run(
            ["yt-dlp", url, "-o", raw_file],
            check=True,
        )

        if not os.path.exists(raw_file):
            raise Exception("No se descargó el archivo")

        # 2️⃣ Convertir SI O SI a MP4 (H.264 compatible)
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

        # 3️⃣ Limpieza con delay (después de descargar)
        if background_tasks:
            background_tasks.add_task(
                limpiar_archivos,
                raw_file,
                final_file,
            )

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
