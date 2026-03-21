#!/usr/bin/env python3
"""
YouTube Video Downloader
Faça download de vídeos do YouTube passando apenas o link.

Dependências (instaladas automaticamente):
    - yt-dlp: Biblioteca para download de vídeos
    - FFmpeg: Necessário para merge de áudio+vídeo e conversão MP3 (externo)

Uso:
    python youdownload.py                        # Modo interativo (menu)
    python youdownload.py <url> [qualidade]      # Modo direto via linha de comando
    python youdownload.py <url> --list-formats   # Lista formatos disponíveis

Qualidades disponíveis: melhor, 720p, 480p, 360p, audio
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


# --- Constantes ---
YOUTUBE_URL_REGEX = re.compile(
    r"^https?://(www\.)?"
    r"(youtube\.com/(watch\?.*v=|shorts/|embed/)|youtu\.be/)"
    r"[a-zA-Z0-9_-]{11}"
    r"([?&].*)?$"
)

QUALIDADES_VALIDAS = {"melhor", "720p", "480p", "360p", "audio"}

MSG_YTDLP_INSTALADO = "✅ 'yt-dlp' instalado com sucesso!\n"
MSG_URL_INVALIDA = "❌ URL inválida. Forneça um link válido do YouTube."

PASTA_SCRIPT = Path(__file__).resolve().parent
PASTA_DOWNLOADS = PASTA_SCRIPT / "downloads"
PASTA_VENV = PASTA_SCRIPT / ".venv"


# --- Gerenciamento automático de dependências (Windows / macOS / Linux) ---
def _python_do_venv() -> Path:
    """Retorna o caminho do executável Python dentro do venv (multiplataforma)."""
    if sys.platform == "win32":
        return PASTA_VENV / "Scripts" / "python.exe"
    return PASTA_VENV / "bin" / "python3"


def _estamos_no_venv() -> bool:
    """Verifica se o interpretador atual já é o do venv do projeto."""
    venv_python = _python_do_venv()
    try:
        return venv_python.resolve() == Path(sys.executable).resolve()
    except OSError:
        return False


def _criar_venv() -> None:
    """Cria um ambiente virtual na pasta do script."""
    import venv

    print("📁 Criando ambiente virtual (.venv)...")
    venv.create(str(PASTA_VENV), with_pip=True)
    print("✅ Ambiente virtual criado.")


def _instalar_no_venv(pacote: str) -> None:
    """Instala um pacote dentro do venv do projeto."""
    venv_python = _python_do_venv()
    print(f"📦 Instalando '{pacote}' no ambiente virtual...")
    subprocess.check_call(
        [str(venv_python), "-m", "pip", "install", "--quiet", pacote],
        timeout=120,  # Evita bloqueio indefinido em caso de rede instável
    )


def _reexecutar_no_venv() -> None:
    """Re-executa o script usando o Python do venv (multiplataforma)."""
    venv_python = str(_python_do_venv())
    print("🔄 Reexecutando com o ambiente virtual...\n")
    if sys.platform == "win32":
        # No Windows, os.execv não funciona bem — usa-se subprocess
        # sys.argv é controlado internamente (re-execução do próprio script)
        resultado = subprocess.run([venv_python] + sys.argv)  # noqa: S603
        sys.exit(resultado.returncode)
    else:
        import os
        # sys.argv é controlado internamente (re-execução do próprio script)
        os.execv(venv_python, [venv_python] + sys.argv)  # noqa: S606


def _instalar_pip_direto(pacote: str) -> bool:
    """Tenta instalar diretamente via pip (funciona se não houver PEP 668)."""
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "--quiet", pacote],
            stdout=subprocess.DEVNULL,
            # Mantém o stderr visível para diagnóstico, suprimindo apenas o stdout
            timeout=120,  # Evita bloqueio indefinido em caso de rede instável
        )
        return True
    except (subprocess.CalledProcessError, OSError):
        return False


def garantir_dependencias() -> None:
    """Verifica e instala automaticamente as dependências Python necessárias."""
    try:
        import yt_dlp  # noqa: F401
        _verificar_ffmpeg()
        return
    except ImportError:
        pass

    print("⚠️  O módulo 'yt-dlp' não foi encontrado.\n")

    # Estratégia 1: Se já estamos no venv, instalar diretamente
    if _estamos_no_venv():
        try:
            _instalar_no_venv("yt-dlp")
            print(MSG_YTDLP_INSTALADO)
            _verificar_ffmpeg()
            return
        except (subprocess.CalledProcessError, OSError) as erro:
            print(f"❌ Falha ao instalar no venv: {erro}")
            sys.exit(1)

    # Estratégia 2: Tentar pip install direto (funciona no Windows e alguns Linux)
    if _instalar_pip_direto("yt-dlp"):
        print(MSG_YTDLP_INSTALADO)
        _verificar_ffmpeg()
        return

    # Estratégia 3: Criar venv, instalar lá, e reexecutar o script
    print("ℹ️  Instalação direta bloqueada pelo sistema (PEP 668).")
    print("   Configurando um ambiente virtual automático...\n")
    try:
        if not PASTA_VENV.exists():
            _criar_venv()
        _instalar_no_venv("yt-dlp")
        print(MSG_YTDLP_INSTALADO)
        _reexecutar_no_venv()
    except (subprocess.CalledProcessError, OSError) as erro:
        print(f"\n❌ Falha ao configurar o ambiente: {erro}")
        print("   Instale manualmente:")
        print("     python3 -m venv .venv")
        if sys.platform == "win32":
            print("     .venv\\Scripts\\activate")
        else:
            print("     source .venv/bin/activate")
        print("     pip install yt-dlp")
        sys.exit(1)


def _verificar_ffmpeg() -> None:
    """Avisa o usuário se o FFmpeg não estiver instalado."""
    if shutil.which("ffmpeg"):
        return
    print("⚠️  FFmpeg não encontrado no sistema.")
    print("   Sem o FFmpeg, o merge de áudio+vídeo ou a conversão para MP3 pode falhar.")
    if sys.platform == "darwin":
        print("   → Instale com: brew install ffmpeg")
    elif sys.platform.startswith("linux"):
        print("   → Instale com: sudo apt install ffmpeg")
    elif sys.platform == "win32":
        print("   → Instale com: winget install ffmpeg")
        print("     Ou baixe em: https://ffmpeg.org/download.html")
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
        print(MSG_URL_INVALIDA)
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
        pasta_destino:  Pasta onde o vídeo será salvo.

    Raises:
        ValueError: Se a URL ou qualidade fornecidas forem inválidas.
        yt_dlp.utils.DownloadError: Se ocorrer um erro durante o download.
    """
    if not validar_url_youtube(url):
        raise ValueError(MSG_URL_INVALIDA)

    # Normaliza a qualidade e valida contra o conjunto permitido
    qualidade = qualidade.lower().strip()
    if qualidade not in QUALIDADES_VALIDAS:
        print(
            f"⚠️  Qualidade '{qualidade}' desconhecida. "
            f"Opções válidas: {', '.join(sorted(QUALIDADES_VALIDAS))}"
        )
        print("   Usando 'melhor' como padrão.\n")
        qualidade = "melhor"

    if pasta_destino is None:
        pasta_destino = PASTA_DOWNLOADS

    pasta_destino.mkdir(parents=True, exist_ok=True)

    formatos: dict[str, str] = {
        "melhor": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "720p":   "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720]",
        "480p":   "bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480]",
        "360p":   "bestvideo[height<=360][ext=mp4]+bestaudio[ext=m4a]/best[height<=360]",
        "audio":  "bestaudio[ext=m4a]/bestaudio",
    }

    formato = formatos[qualidade]  # Acesso direto — qualidade já validada acima

    opcoes: dict[str, Any] = {
        "format": formato,
        "restrictfilenames": True,
        "outtmpl": str(pasta_destino / "%(title)s.%(ext)s"),
        "progress_hooks": [progresso_hook],
        "postprocessors": [],
        "noplaylist": True,
        "socket_timeout": 30,
        "retries": 3,
    }

    # merge_output_format só faz sentido para vídeo; omitir no áudio evita warnings
    if qualidade != "audio":
        opcoes["merge_output_format"] = "mp4"

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
        print("\n🔍 Obtendo informações do vídeo...")
        info = ydl.extract_info(url, download=False)

        if info is None:
            print("❌ Não foi possível obter as informações do vídeo.")
            return

        duracao = info.get("duration")
        print(f"📹 Título:   {info.get('title', 'Desconhecido')}")
        print(f"⏱  Duração:  {formatar_duracao(duracao)}")
        print(f"👤 Canal:    {info.get('channel', 'Desconhecido')}")
        print(f"📂 Destino:  {pasta_destino}")
        print(f"🎯 Qualidade: {qualidade}\n")

        print("⬇️  Iniciando download...\n")
        ydl.download([url])
        print("\n✅ Download concluído com sucesso!")


def progresso_hook(dados: dict[str, Any]) -> None:
    """Callback chamado pelo yt-dlp para exibir o progresso do download."""
    # Usa .get() para evitar KeyError caso o campo 'status' esteja ausente
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
        print("\n  📦 Download do arquivo finalizado, processando...")


def formatar_duracao(segundos: int | float | None) -> str:
    """
    Converte segundos para formato legível (ex: '5m 20s').

    Aceita int ou float (a API do yt-dlp pode retornar float).
    """
    if not segundos:  # Cobre None e 0
        return "Desconhecida"
    total_segs = int(segundos)  # Garante que é inteiro antes de divmod
    horas, resto = divmod(total_segs, 3600)
    minutos, segs = divmod(resto, 60)
    if horas > 0:
        return f"{horas}h {minutos}m {segs}s"
    return f"{minutos}m {segs}s"


def menu() -> None:
    """Menu interativo para o usuário."""
    print("=" * 50)
    print("  🎬 YouTube Video Downloader")
    print("=" * 50)

    url = input("\n📎 Cole o link do vídeo: ").strip()

    if not url:
        print("❌ Nenhum link fornecido.")
        return

    if not validar_url_youtube(url):
        print(MSG_URL_INVALIDA)
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
    except ValueError as erro:
        print(f"\n❌ Erro de validação: {erro}")
    except yt_dlp.utils.DownloadError as erro:
        print(f"\n❌ Erro no download: {erro}")
    except KeyboardInterrupt:
        print("\n\n⚠️  Download cancelado pelo usuário.")


def _usar_modo_cli(args: list[str]) -> None:
    """Processa os argumentos da linha de comando e inicia a ação correspondente."""
    url = args[0]

    if not validar_url_youtube(url):
        print(MSG_URL_INVALIDA)
        sys.exit(1)

    # Suporte ao flag --list-formats
    if len(args) > 1 and args[1] == "--list-formats":
        listar_formatos(url)
        return

    qualidade = args[1] if len(args) > 1 else "melhor"

    try:
        download_video(url, qualidade)
    except ValueError as erro:
        print(f"\n❌ Erro de validação: {erro}")
        sys.exit(1)
    except yt_dlp.utils.DownloadError as erro:
        print(f"\n❌ Erro no download: {erro}")
        sys.exit(1)


if __name__ == "__main__":
    try:
        if len(sys.argv) > 1:
            _usar_modo_cli(sys.argv[1:])
        else:
            menu()
    except KeyboardInterrupt:
        print("\n\n⚠️  Cancelado pelo usuário.")
        sys.exit(0)
