import subprocess
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os
from yt_dlp import YoutubeDL
import re

# Inicializando o aplicativo FastAPI
app = FastAPI()

# Configuração do CORS para permitir requisições externas (ajuste os domínios permitidos se necessário)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Para segurança, troque '*' por domínios específicos, como ['http://localhost:3000']
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos os métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permite todos os cabeçalhos
)

# Token de autenticação (substitua por um valor seguro)
AUTH_TOKEN = "c5cca4d2-8e94-4512-bb59-004129018495"

# Modelo para receber a URL do vídeo e a pasta de saída
class DownloadRequest(BaseModel):
    video_url: str
    output_folder: str = "downloads"  # Diretório padrão
    token: str  # Token de autenticação

# Função para validar o token
def verify_token(token: str):
    if token != AUTH_TOKEN:
        raise HTTPException(status_code=403, detail="Token inválido")

# Função para extrair o ID do vídeo da URL
def extract_video_id(video_url: str):
    pattern = r"(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:v\/|watch\?v=|embed\/|shorts\/)|youtu\.be\/)([a-zA-Z0-9_-]{11})"
    match = re.search(pattern, video_url)
    if not match:
        raise HTTPException(status_code=400, detail="URL inválida")
    return match.group(1)

# Função para baixar áudio como MP3, verificando se já existe antes
def downloadAudioAsMp3(video_url: str, output_folder: str):
    try:
        # Criar a pasta de saída se não existir
        os.makedirs(output_folder, exist_ok=True)

        # Extrair o ID do vídeo da URL
        video_id = extract_video_id(video_url)
        filename = os.path.join(output_folder, f"{video_id}.mp3")

        # Verificar se o arquivo já existe
        if os.path.exists(filename):
            # Arquivo já existe, envia para o Firebase também
            message = "Áudio já baixado!"
        else:
            # Configuração do yt-dlp para baixar o áudio
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'outtmpl': os.path.join(output_folder, '%(id)s.%(ext)s'),
                'cookiefile': 'cookies.firefox-private.txt',
            }

            # Baixar o áudio
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])

            message = "Áudio baixado com sucesso!"

        # Enviar o arquivo para o Firebase (sempre que o arquivo for encontrado ou baixado)
        file_path = filename
        command = ['node', './exportMp3ToFirebase.js', file_path]

        try:
            # Executa o comando Node.js e captura a saída
            result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            # A saída do script Node.js
            nodejs_output = result.stdout.strip()  # Remover qualquer quebra de linha extra
        except subprocess.CalledProcessError as e:
            print(f"Ocorreu um erro ao executar o script: {e.stderr}")
            nodejs_output = f"Erro ao executar o script Node.js: {e.stderr.strip()}"

        # Retorna a resposta com a mensagem e a saída do script Node.js
        return {
            "message": message,
            "file_url": f"/downloads/{video_id}.mp3",
            "firebase_response": nodejs_output  # Resposta do script Node.js
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao baixar o áudio: {e}")

# Endpoint para baixar o áudio
@app.post("/download-audio/")
async def download_audio(request: DownloadRequest):
    verify_token(request.token)  # Verifica se o token é válido
    return downloadAudioAsMp3(request.video_url, request.output_folder)

# Servindo arquivos estáticos (para acessar os MP3 baixados)
if not os.path.exists("downloads"):
    os.makedirs("downloads")

app.mount("/downloads", StaticFiles(directory="downloads", html=False), name="downloads")

# sudo systemctl restart youtube-download
