# Relatório de Code Review — YouDownload

Revisão do arquivo [youdownload.py](file:///Users/ricardosantos/Documents/YouDownload/youdownload.py).

---

## 🐛 Bugs Corrigidos

### 1. Acesso direto a chave de dicionário em `progresso_hook` (KeyError)

```diff
- if d["status"] == "downloading":   # ❌ KeyError se 'status' estiver ausente
+ status = dados.get("status")       # ✅ Retorna None sem exceção
+ if status == "downloading":
```

O yt-dlp pode chamar o hook com dicionários incompletos (ex: ao cancelar). O acesso direto `d["status"]` levantava `KeyError`.

---

### 2. `formatar_duracao` não tratava tipo `float`

```diff
- def formatar_duracao(segundos: int | None) -> str:
+ def formatar_duracao(segundos: int | float | None) -> str:
+     total_segs = int(segundos)  # Converte float -> int antes do divmod
+     horas, resto = divmod(total_segs, 3600)
```

A API do yt-dlp retorna `duration` como `float`. Passar um float ao `divmod` funciona, mas pode gerar saídas como `"5m 20.0s"`. A conversão explícita previne isso.

---

### 3. Validação de URL ausente no modo CLI

```diff
- # Antes: sys.argv[1] era passado direto para download_video() sem validar
+ if not validar_url_youtube(url):
+     print("❌ URL inválida.")
+     sys.exit(1)
```

Se o utilizador passasse uma URL inválida via linha de comandos, o erro só seria detectado dentro de `yt-dlp`, com mensagem confusa.

---

### 4. `merge_output_format: None` passado explicitamente ao yt-dlp

```diff
- "merge_output_format": "mp4" if qualidade != "audio" else None,
+ if qualidade != "audio":
+     opcoes["merge_output_format"] = "mp4"
```

Passar uma chave com valor `None` pode gerar warnings internos no yt-dlp. A opção só deve existir no dicionário quando tem um valor válido.

---

### 5. Qualidade inválida via CLI era silenciosamente ignorada

```diff
- qualidade = sys.argv[2] if len(sys.argv) > 2 else "melhor"
# Qualidade inválida → "melhor" usado sem aviso
+ qualidade = args[1] if len(args) > 1 else "melhor"
# download_video agora valida e avisa o utilizador
```

---

## 🔐 Segurança e Boas Práticas

### 6. `requirements.txt` sem versão pinada

```diff
- yt-dlp
+ yt-dlp>=2026.3.3
```

Sem pin de versão, `pip install -r requirements.txt` pode instalar versões com vulnerabilidades conhecidas. Usar `>=versão_atual` garante um baseline mínimo seguro.

---

### 7. `_instalar_pip_direto` suprimia o stderr completamente

```diff
- stderr=subprocess.DEVNULL,  # ❌ Erros de instalação invisíveis
+ # stderr não suprimido → erros de pip ficam visíveis para diagnóstico
```

Suprimir stderr escondia mensagens de erro do pip (ex: conflitos de dependências, erros de rede), dificultando diagnóstico.

---

### 8. `download_video` usava `print` para erros de validação em vez de `raise`

```diff
- print("❌ URL inválida.")
- return
+ raise ValueError("URL inválida. Forneça um link válido do YouTube.")
```

Funções chamadas programaticamente devem levantar exceções em vez de imprimir e retornar silenciosamente. Os pontos de entrada (`menu`, `_usar_modo_cli`) capturam e exibem a mensagem ao utilizador.

---

## ✨ Melhorias Adicionais

### 9. Tipo genérico específico em vez de `dict` nu

```diff
- opcoes: dict = { ... }
+ from typing import Any
+ opcoes: dict[str, Any] = { ... }
+ formatos: dict[str, str] = { ... }
```

`dict` sem parâmetros é um type hint impreciso. `dict[str, Any]` documenta claramente a estrutura esperada.

---

### 10. Constante `QUALIDADES_VALIDAS` para validação centralizada

```python
QUALIDADES_VALIDAS = {"melhor", "720p", "480p", "360p", "audio"}
```

Evita duplicação da lógica de validação e torna mais fácil adicionar novas qualidades no futuro.

---

### 11. Extração do modo CLI para função dedicada `_usar_modo_cli`

```python
def _usar_modo_cli(args: list[str]) -> None:
    ...
```

O bloco `if __name__ == "__main__"` fica mais limpo e testável. Também adiciona suporte ao flag `--list-formats` via CLI.

---

### 12. Acesso direto à chave validada no dict de formatos

```diff
- formato = formatos.get(qualidade, formatos["melhor"])
+ formato = formatos[qualidade]  # Seguro: qualidade já foi validada
```

Como a qualidade é validada contra `QUALIDADES_VALIDAS` antes desta linha, o `.get()` com fallback é redundante e mascarava bugs potenciais.

---

### 13. Docstring melhorada em `download_video`

Adicionada secção `Raises` para documentar explicitamente quais exceções podem ser levantadas.

---

## 📋 Resumo das Alterações

| Ficheiro | Tipo | Descrição |
|---|---|---|
| `youdownload.py` | MODIFY | Bugs corrigidos, boas práticas aplicadas, melhorias de robustez |
| `requirements.txt` | MODIFY | Versão mínima do yt-dlp pinada |
