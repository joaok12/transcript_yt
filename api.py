import logging
import re
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from youtube_transcript_api import YouTubeTranscriptApi

# Configuração básica do logging
logging.basicConfig(level=logging.INFO)

app = FastAPI()

# Permitir acesso de qualquer origem
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_video_id(url: str):
    """
    Extrai o ID do vídeo a partir da URL do YouTube.
    """
    match = re.search(r"v=([a-zA-Z0-9_-]+)", url)
    return match.group(1) if match else None

@app.get("/transcription/")
async def get_transcription(url: str):
    """
    Endpoint para obter a transcrição do vídeo.
    """
    video_id = get_video_id(url)
    if not video_id:
        raise HTTPException(status_code=400, detail="URL inválida!")
    
    try:
        logging.info(f"Obtendo transcrição para o vídeo: {video_id}")
        # Tenta obter a transcrição usando os idiomas 'pt' e 'en'
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['pt', 'en'])
        text = " ".join([t["text"] for t in transcript])
        return {"transcription": text}
    except Exception as e:
        logging.error(f"Erro ao obter a transcrição para {video_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao obter a transcrição: {str(e)}")
