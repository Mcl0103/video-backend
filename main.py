from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uuid
import subprocess
import os

app = FastAPI()

# Permitir llamadas desde cualquier web
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
    video_id = str(uuid.uuid4())
    output_file = f"{video_id}.mp4"

    try:
        subprocess.run(
            [
                "yt-dlp",
                "-f",
                "mp4",
                "-o",
                output_file,
                data.url,
            ],
            check=True,
        )

        return FileResponse(
            path=output_file,
            filename="video.mp4",
            media_type="video/mp4",
        )

    except Exception as e:
        return {"error": str(e)}
