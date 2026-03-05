#!/usr/bin/env python3
"""
YouTube Video Downloader
Faça download de vídeos do YouTube passando apenas o link.

Dependências (instaladas automaticamente):
    - yt-dlp: Biblioteca para download de vídeos
    - FFmpeg: Necessário para merge de áudio+vídeo e conversão MP3 (externo)
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path


# --- Constantes ---
YOUTUBE_URL_REGEX = re.compile(
    r"^https?://(www\.)?"
    r"(youtube\.com/(watch\?.*v=|shorts/|embed/)|youtu\.be/)"
    r"[a-zA-Z0-9_-]{11}"
)

PASTA_DOWNLOADS = Path(__file__).resolve().parent / "downloads"


# --- Gestão automática de dependências ---
def _instalar_pacote(pacote: str) -> None:
    """Instala um pacote Python usando o pip do interpretador atual.

    Estratégia por sistema operativo:
      - Windows : pip normal (sem restrições de sistema)
      - macOS   : tenta pip normal; se falhar (Homebrew/externally-managed),
                  repete com --break-system-packages
      - Linux   : tenta pip normal; se falhar (PEP 668 / apt-managed),
                  repete com --break-system-packages
    """
    print(f"📦 A instalar '{pacote}'...")
    cmd_base = [sys.executable, "-m", "pip", "install", "--quiet", pacote]

    if sys.platform == "win32":
        # Windows não tem restrições de «externally-managed environment»
        subprocess.check_call(
            cmd_base,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    else:
        # macOS (Homebrew) e Linux (apt/dnf-managed) podem bloquear pip normal
        try:
            subprocess.check_call(
                cmd_base,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except subprocess.CalledProcessError:
            # PEP 668 / externally-managed-environment: tentar com a flag adequada
            subprocess.check_call(
                cmd_base + ["--break-system-packages"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )


def garantir_dependencias() -> None:
    """Verifica e instala automaticamente as dependências Python necessárias."""
    try:
        import yt_dlp  # noqa: F401
    except ImportError:
        print("⚠️  O módulo 'yt-dlp' não foi encontrado.")
        try:
            _instalar_pacote("yt-dlp")
            print("✅ 'yt-dlp' instalado com sucesso!\n")
        except (subprocess.CalledProcessError, OSError) as erro:
            print(f"❌ Falha ao instalar 'yt-dlp': {erro}")
            print("   Instale manualmente: pip install yt-dlp")
            sys.exit(1)

    if not shutil.which("ffmpeg"):
        print("⚠️  FFmpeg não encontrado no sistema.")
        print("   Sem FFmpeg, merge de áudio+vídeo ou conversão MP3 podem falhar.")
        if sys.platform == "darwin":
            print("   → Instale com: brew install ffmpeg")
        elif sys.platform.startswith("linux"):
            print("   → Instale com: sudo apt install ffmpeg")
        elif sys.platform == "win32":
            print("   → Baixe em: https://ffmpeg.org/download.html")
        print()


garantir_dependencias()

import yt_dlp  # noqa: E402


# --- Validação ---
def validar_url_youtube(url: str) -> bool:
    """Verifica se a URL é um link válido do YouTube."""
    return bool(YOUTUBE_URL_REGEX.match(url))


def listar_formatos(url: str) -> None:
    """Lista os formatos de download disponíveis para o vídeo."""
    if not validar_url_youtube(url):
        print("❌ URL inválida. Forneça um link válido do YouTube.")
        return

    with yt_dlp.YoutubeDL({"listformats": True, "quiet": True}) as ydl:
        ydl.download([url])


def download_video(
    url: str,
    qualidade: str = "melhor",
    pasta_destino: Path | None = None,
) -> None:
    """
    Faz o download do vídeo do YouTube.

    Args:
        url:            Link do vídeo do YouTube.
        qualidade:      'melhor', '720p', '480p', '360p' ou 'audio'.
        pasta_destino:  Pasta onde o vídeo será guardado.
    """
    if not validar_url_youtube(url):
        print("❌ URL inválida. Forneça um link válido do YouTube.")
        return

    if pasta_destino is None:
        pasta_destino = PASTA_DOWNLOADS

    pasta_destino.mkdir(parents=True, exist_ok=True)

    tem_ffmpeg = bool(shutil.which("ffmpeg"))

    # Formatos com fallbacks progressivos: tenta mp4/m4a primeiro,
    # depois aceita qualquer codec, por fim aceita qualquer formato único.
    # Sem FFmpeg não é possível fazer merge de streams separados,
    # por isso o último fallback é sempre um formato já combinado ("best").
    if tem_ffmpeg:
        formatos = {
            "melhor": (
                "bestvideo[ext=mp4]+bestaudio[ext=m4a]"
                "/bestvideo+bestaudio"
                "/best"
            ),
            "720p": (
                "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]"
                "/bestvideo[height<=720]+bestaudio"
                "/best[height<=720]"
                "/best"
            ),
            "480p": (
                "bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]"
                "/bestvideo[height<=480]+bestaudio"
                "/best[height<=480]"
                "/best"
            ),
            "360p": (
                "bestvideo[height<=360][ext=mp4]+bestaudio[ext=m4a]"
                "/bestvideo[height<=360]+bestaudio"
                "/best[height<=360]"
                "/best"
            ),
            "audio": "bestaudio[ext=m4a]/bestaudio/best",
        }
    else:
        # Sem FFmpeg: usar apenas formatos já combinados (sem merge)
        formatos = {
            "melhor": "best[ext=mp4]/best",
            "720p":   "best[height<=720][ext=mp4]/best[height<=720]/best",
            "480p":   "best[height<=480][ext=mp4]/best[height<=480]/best",
            "360p":   "best[height<=360][ext=mp4]/best[height<=360]/best",
            "audio":  "bestaudio[ext=m4a]/bestaudio/best",
        }

    formato = formatos.get(qualidade, formatos["melhor"])

    opcoes: dict = {
        "format": formato,
        "restrictfilenames": True,
        "outtmpl": str(pasta_destino / "%(title)s.%(ext)s"),
        "merge_output_format": "mp4" if (qualidade != "audio" and tem_ffmpeg) else None,
        "progress_hooks": [progresso_hook],
        "postprocessors": [],
        "noplaylist": True,
        "socket_timeout": 30,
        "retries": 3,
    }

    if qualidade == "audio":
        if not shutil.which("ffmpeg"):
            print("❌ FFmpeg é necessário para converter áudio em MP3.")
            print("   Instale o FFmpeg e tente novamente.")
            return
        opcoes["postprocessors"].append({
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        })

    with yt_dlp.YoutubeDL(opcoes) as ydl:
        print("\n🔍 A obter informações do vídeo...")
        info = ydl.extract_info(url, download=False)

        if info is None:
            print("❌ Não foi possível obter informações do vídeo.")
            return

        print(f"📹 Título: {info.get('title', 'Desconhecido')}")
        print(f"⏱  Duração: {formatar_duracao(info.get('duration'))}")
        print(f"👤 Canal: {info.get('channel', 'Desconhecido')}")
        print(f"📂 Destino: {pasta_destino}")
        print(f"🎯 Qualidade: {qualidade}\n")

        print("⬇️  A iniciar download...\n")
        ydl.download([url])
        print("\n✅ Download concluído com sucesso!")


def progresso_hook(dados: dict) -> None:
    """Callback chamado pelo yt-dlp para mostrar o progresso do download."""
    status = dados.get("status")
    if status == "downloading":
        percentual = dados.get("_percent_str", "N/A")
        velocidade = dados.get("_speed_str", "N/A")
        tempo_restante = dados.get("_eta_str", "N/A")
        print(
            f"\r  ⏳ {percentual} | Velocidade: {velocidade} | Restante: {tempo_restante}",
            end="",
            flush=True,
        )
    elif status == "finished":
        print("\n  📦 Download do ficheiro finalizado, a processar...")


def formatar_duracao(segundos: int | None) -> str:
    """Converte segundos para formato legível (ex: '5m 20s')."""
    if not segundos:
        return "Desconhecida"
    horas, resto = divmod(segundos, 3600)
    minutos, segs = divmod(resto, 60)
    if horas > 0:
        return f"{horas}h {minutos}m {segs}s"
    return f"{minutos}m {segs}s"


def menu() -> None:
    """Menu interativo para o utilizador."""
    print("=" * 50)
    print("  🎬 YouTube Video Downloader")
    print("=" * 50)

    url = input("\n📎 Cole o link do vídeo: ").strip()

    if not url:
        print("❌ Nenhum link fornecido.")
        return

    if not validar_url_youtube(url):
        print("❌ URL inválida. Forneça um link válido do YouTube.")
        return

    print("\n📊 Escolha a qualidade:")
    print("  1 - Melhor qualidade disponível")
    print("  2 - 720p (HD)")
    print("  3 - 480p")
    print("  4 - 360p")
    print("  5 - Apenas áudio (MP3)")

    escolha = input("\nOpção [1]: ").strip() or "1"

    opcoes_qualidade = {
        "1": "melhor",
        "2": "720p",
        "3": "480p",
        "4": "360p",
        "5": "audio",
    }

    qualidade = opcoes_qualidade.get(escolha, "melhor")

    try:
        download_video(url, qualidade)
    except yt_dlp.utils.DownloadError as erro:
        print(f"\n❌ Erro no download: {erro}")
    except KeyboardInterrupt:
        print("\n\n⚠️  Download cancelado pelo utilizador.")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        link = sys.argv[1]
        qualidade = sys.argv[2] if len(sys.argv) > 2 else "melhor"
        try:
            download_video(link, qualidade)
        except yt_dlp.utils.DownloadError as erro:
            print(f"\n❌ Erro no download: {erro}")
    else:
        menu()
