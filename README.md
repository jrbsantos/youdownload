# 🎬 YouDownload

Um downloader de vídeos do YouTube simples, rápido e multiplataforma, feito em Python.

## ✨ Funcionalidades

- 📥 Download de vídeos em diversas qualidades (melhor, 720p, 480p, 360p)
- 🎵 Extração de áudio em **MP3** (192kbps)
- 🖥️ Modo interativo com menu amigável
- ⚡ Modo direto via linha de comando (CLI)
- 🔍 Listagem de todos os formatos disponíveis do vídeo
- 🤖 Gerenciamento automático de dependências (cria e usa `.venv` automaticamente)
- 🌍 Compatível com **Windows**, **macOS** e **Linux**

## 📋 Pré-requisitos

- Python 3.8+
- [FFmpeg](https://ffmpeg.org/) — necessário para merge de áudio+vídeo e conversão para MP3

### Instalando o FFmpeg

| Sistema | Comando |
|---|---|
| macOS | `brew install ffmpeg` |
| Linux (Debian/Ubuntu) | `sudo apt install ffmpeg` |
| Windows | `winget install ffmpeg` ou [baixe aqui](https://ffmpeg.org/download.html) |

## 🚀 Instalação

```bash
# Clone o repositório
git clone https://github.com/jrbsantos/youdownload.git
cd youdownload
```

> As dependências Python (`yt-dlp`) são instaladas **automaticamente** na primeira execução.
> Não é necessário rodar `pip install` manualmente.

## 🎯 Como usar

### Modo interativo (menu)

```bash
python youdownload.py
```

O menu vai guiar você pelo processo:

```
==================================================
  🎬 YouTube Video Downloader
==================================================

📎 Cole o link do vídeo: https://www.youtube.com/watch?v=...

📊 Escolha a qualidade:
  1 - Melhor qualidade disponível
  2 - 720p (HD)
  3 - 480p
  4 - 360p
  5 - Apenas áudio (MP3)
```

### Modo linha de comando (CLI)

```bash
# Melhor qualidade disponível
python youdownload.py <url>

# Qualidade específica
python youdownload.py <url> 720p
python youdownload.py <url> 480p
python youdownload.py <url> 360p

# Apenas áudio (MP3)
python youdownload.py <url> audio

# Listar todos os formatos disponíveis
python youdownload.py <url> --list-formats
```

**Qualidades disponíveis:** `melhor` · `720p` · `480p` · `360p` · `audio`

## 📂 Estrutura do projeto

```
youdownload/
├── youdownload.py      # Script principal
├── requirements.txt    # Dependências do projeto
├── downloads/          # Pasta onde os vídeos são salvos (criada automaticamente)
├── .venv/              # Ambiente virtual (criado automaticamente)
└── .gitignore
```

## 📦 Dependências

| Pacote | Versão mínima | Descrição |
|---|---|---|
| [yt-dlp](https://github.com/yt-dlp/yt-dlp) | 2026.3.3 | Motor de download de vídeos |
| FFmpeg | — | Merge de streams e conversão de áudio (externo) |

## 📝 Licença

Este projeto é de uso livre para fins educacionais e pessoais.
