import streamlit as st
import subprocess
import os
import re
from yt_dlp import YoutubeDL

# Título do aplicativo
st.title("Baixar Áudio do YouTube como MP3")

# Token de autenticação (substitua por um valor seguro)
AUTH_TOKEN = "c5cca4d2-8e94-4512-bb59-004129018495"

# Diretório padrão para salvar os arquivos
OUTPUT_FOLDER = "downloads"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Função para extrair o ID do vídeo da URL
def extract_video_id(video_url: str):
    pattern = r"(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:v\/|watch\?v=|embed\/|shorts\/)|youtu\.be\/)([a-zA-Z0-9_-]{11})"
    match = re.search(pattern, video_url)
    if not match:
        return None
    return match.group(1)

# Função para baixar áudio como MP3
def download_audio_as_mp3(video_url: str):
    video_id = extract_video_id(video_url)
    if not video_id:
        st.error("URL inválida. Insira uma URL válida do YouTube.")
        return None

    filename = os.path.join(OUTPUT_FOLDER, f"{video_id}.mp3")

    if os.path.exists(filename):
        st.warning("O áudio já foi baixado anteriormente.")
        return filename

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': os.path.join(OUTPUT_FOLDER, '%(id)s.%(ext)s'),
        'cookiefile': 'cookies.firefox-private.txt',
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        return filename
    except Exception as e:
        st.error(f"Erro ao baixar o áudio: {e}")
        return None

# Campo para inserir a URL do vídeo
video_url = st.text_input("Insira a URL do vídeo do YouTube:")

# Campo para inserir o token de autenticação
token = st.text_input("Insira o token de autenticação:", type="password")

# Botão para baixar o áudio
if st.button("Baixar Áudio"):
    if token != AUTH_TOKEN:
        st.error("Token inválido. Acesso negado.")
    elif video_url:
        st.info("Baixando áudio, aguarde...")
        file_path = download_audio_as_mp3(video_url)
        if file_path:
            st.success("Download concluído!")
            st.audio(file_path, format="audio/mp3")
            st.download_button("Baixar MP3", file_path, file_name=os.path.basename(file_path))
    else:
        st.warning("Por favor, insira uma URL válida.")

