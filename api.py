from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from youtube_transcript_api import YouTubeTranscriptApi
import re

app = FastAPI()

# Permitir chamadas do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_video_id(url: str):
    """Extrai o ID do vídeo a partir da URL do YouTube."""
    match = re.search(r"v=([a-zA-Z0-9_-]+)", url)
    return match.group(1) if match else None

@app.get("/transcription/")
async def get_transcription(url: str):
    """Obtém a transcrição do vídeo."""
    video_id = get_video_id(url)
    
    if not video_id:
        raise HTTPException(status_code=400, detail="URL inválida!")
    
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['pt', 'en'])
        text = " ".join([t["text"] for t in transcript])
        return {"transcription": text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter a transcrição: {str(e)}")
