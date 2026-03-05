# 🎬 YouDownload

Um script Python simples e poderoso para fazer download de vídeos e áudio do YouTube diretamente pela linha de comando. Suporta vídeos normais, Shorts e links `youtu.be`. Instala as dependências automaticamente na primeira execução.

---

## ✨ Funcionalidades

- 📥 Download de vídeos em múltiplas qualidades: **melhor**, **720p**, **480p**, **360p**
- 🎵 Extração de **áudio em MP3** (192kbps)
- ▶️ Suporte a **YouTube Shorts**, vídeos normais e links encurtados (`youtu.be`)
- 📦 **Instalação automática** do `yt-dlp` na primeira execução
- 🖥️ Modo **interativo** (menu) ou modo **linha de comandos** com argumentos
- 📊 Barra de progresso em tempo real com velocidade e tempo restante
- 🔁 Fallback automático de formatos — funciona com ou sem FFmpeg
- 🌍 Compatível com **macOS**, **Linux** (incluindo WSL) e **Windows**

---

## ⚙️ Requisitos

| Requisito | Versão mínima | Notas |
|-----------|--------------|-------|
| Python | **3.12+** | Verificado automaticamente |
| yt-dlp | Qualquer | Instalado automaticamente |
| FFmpeg | Qualquer | **Opcional** — necessário para melhor qualidade e conversão MP3 |

> ⚠️ Sem FFmpeg o script ainda funciona, mas usará apenas formatos já combinados (qualidade ligeiramente inferior).

---

## 🚀 Instalação

### 1. Clonar o repositório

```bash
git clone https://github.com/seu-usuario/youdownload.git
cd youdownload
```

### 2. (Opcional, mas recomendado) Instalar o FFmpeg

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu / Debian / WSL:**
```bash
sudo apt install ffmpeg
```

**Windows:**
Baixe em [ffmpeg.org/download.html](https://ffmpeg.org/download.html) e adicione ao `PATH`.

### 3. Pronto!

O `yt-dlp` é instalado automaticamente na primeira vez que o script é executado.

---

## 📖 Utilização

### Modo linha de comandos

```bash
python3 youdownload.py <URL> [qualidade]
```

**Exemplos:**

```bash
# Melhor qualidade disponível (padrão)
python3 youdownload.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# 720p HD
python3 youdownload.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ" 720p

# Apenas áudio em MP3
python3 youdownload.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ" audio

# YouTube Shorts
python3 youdownload.py "https://www.youtube.com/shorts/Gq1KLZyckd0"

# Link encurtado
python3 youdownload.py "https://youtu.be/dQw4w9WgXcQ" 480p
```

### Qualidades disponíveis

| Argumento | Descrição |
|-----------|-----------|
| `melhor` | Melhor qualidade disponível *(padrão)* |
| `720p` | HD 720p |
| `480p` | SD 480p |
| `360p` | SD 360p |
| `audio` | Apenas áudio, exportado em MP3 192kbps |

> ❌ Passar um valor de qualidade inválido termina o script imediatamente com uma mensagem de erro indicando as opções válidas.

### Modo interativo (menu)

Execute sem argumentos para aceder ao menu interativo:

```bash
python3 youdownload.py
```

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

Opção [1]:
```

---

## 📂 Estrutura do projeto

```
youdownload/
├── youdownload.py   # Script principal
├── downloads/       # Pasta criada automaticamente com os ficheiros descarregados
└── README.md
```

---

## 🔧 Como funciona

1. **Verificação de Python** — O script verifica se está a correr em Python 3.12+. Caso contrário, exibe uma mensagem clara e termina.
2. **Gestão de dependências** — Tenta importar `yt-dlp`. Se não estiver instalado, instala automaticamente via `pip`, com suporte a ambientes geridos pelo sistema (Homebrew, apt, etc.).
3. **Verificação de FFmpeg** — Avisa se o FFmpeg não estiver disponível e ajusta os formatos de download automaticamente.
4. **Download adaptativo** — Usa uma cadeia de formatos com fallbacks progressivos para garantir que o download funciona independentemente dos formatos disponíveis no vídeo.

---

## 🐛 Problemas conhecidos / FAQ

**O pip falha a instalar o `yt-dlp` no macOS ou Linux?**
> O script tenta automaticamente com `--break-system-packages` em ambientes Homebrew/apt. Se mesmo assim falhar, use um ambiente virtual:
> ```bash
> python3 -m venv venv && source venv/bin/activate
> pip install yt-dlp
> python3 youdownload.py "URL"
> ```

**O download falha com "Requested format is not available"?**
> Certifique-se de que o `yt-dlp` está atualizado:
> ```bash
> pip install -U yt-dlp
> ```

**A conversão para MP3 não funciona?**
> O FFmpeg é obrigatório para extração de áudio. Consulte a secção de instalação acima.

**Funciona no WSL (Windows Subsystem for Linux)?**
> Sim! Certifique-se de usar Python 3.12+ (`python3 --version`) e instale o FFmpeg com `sudo apt install ffmpeg`.

---

## 📜 Licença

MIT License — sinta-se à vontade para usar, modificar e distribuir.
