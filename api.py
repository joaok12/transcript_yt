import logging
import re
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api import TranscriptsDisabled, NoTranscriptFound

# Configuração de logs para diagnosticar problemas
logging.basicConfig(level=logging.INFO)

# >>> MONKEY PATCH para definir um User-Agent customizado
try:
    # A biblioteca utiliza headers padrão definidos em youtube_transcript_api._api
    from youtube_transcript_api import _api
    _api.DEFAULT_HEADERS["User-Agent"] = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/103.0.0.0 Safari/537.36"
    )
    logging.info("User-Agent customizado definido com sucesso!")
except Exception as e:
    logging.error(f"Erro ao definir User-Agent customizado: {e}")

app = FastAPI()

# Permitir requisições de qualquer origem
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
    """
    Endpoint para obter a transcrição do vídeo.
    Tenta buscar as legendas utilizando um User-Agent customizado.
    """
    video_id = get_video_id(url)
    if not video_id:
        raise HTTPException(status_code=400, detail="URL inválida!")
    
    try:
        logging.info(f"Obtendo transcrição para o vídeo: {video_id}")
        # Tenta obter a transcrição sem especificar idiomas
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        text = " ".join([t["text"] for t in transcript])
        return {"transcription": text}
    except (TranscriptsDisabled, NoTranscriptFound) as e:
        logging.error(f"Legendas não disponíveis para {video_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Transcrição não disponível para esse vídeo: {str(e)}")
    except Exception as e:
        logging.error(f"Erro ao obter a transcrição para {video_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao obter a transcrição: {str(e)}")
