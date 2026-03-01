# Mago Invocador 2D (Pygame)

Protótipo de jogo 2D em Python + Pygame com arquitetura modular.

## ✅ Pré-requisitos

- Python **3.11+**
- `pip`

## ✅ Instalação

No terminal aberto na pasta do projeto (`/workspace/projeto-jogo-2d`):

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows PowerShell
pip install -r requirements.txt
```

## ▶️ Como rodar

```bash
python main.py
```

Se tudo estiver correto, abrirá uma janela com o jogo.

## 🎮 Controles

- `A`: mover para esquerda
- `D`: mover para direita
- `ESPAÇO`: pular
- `J`: invocar Mago (projéteis)
- `K`: invocar Guerreiro (curta distância)
- `L`: invocar Carta Explosiva (armadilha)

## 🧩 "No VSCode clico em Run e nada acontece"

Isso geralmente ocorre por um destes motivos:

1. **Interpretador errado** (sem pygame instalado).
   - No VSCode: `Ctrl+Shift+P` → `Python: Select Interpreter` → escolha o Python da `.venv`.
2. **Dependências não instaladas**.
   - Rode: `pip install -r requirements.txt`.
3. **Executando fora da pasta do projeto**.
   - Garanta que `main.py` está na raiz aberta no VSCode.
4. **Run sem terminal visível**.
   - Use o perfil de debug `Rodar main.py (Pygame)` (arquivo `.vscode/launch.json`) para abrir pelo terminal integrado.

## 🐞 Verificação rápida

```bash
python -c "import pygame; print(pygame.ver)"
python main.py
```

Se o primeiro comando falhar, o pygame ainda não foi instalado no ambiente/interpretador atual.
