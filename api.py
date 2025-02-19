from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
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
        # Primeiro, tenta pegar as legendas manuais
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['pt', 'en'])
    except (TranscriptsDisabled, NoTranscriptFound):
        try:
            # Se não houver legendas manuais, tenta pegar legendas automáticas
            transcript = YouTubeTranscriptApi.list_transcripts(video_id).find_generated_transcript(['en']).fetch()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro ao obter a transcrição: {str(e)}")

    text = " ".join([t["text"] for t in transcript])
    return {"transcription": text}
