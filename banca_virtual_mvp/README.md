# Banca Virtual – MVP (Streamlit)

Plataforma genérica de **análise de propostas** e **construção de projetos** para editais de subvenção (ex.: SEEDES, Centelha, TecNova), com:
- **Elegibilidade & Conformidade**
- **Banca Virtual** (pontuação por critérios configuráveis via YAML)
- **Pitch Analyzer** (PDF + transcrição de áudio)
- **Valuation** (Scorecard, VC Method, DCF simples)

## Como rodar localmente
```bash
pip install -r requirements.txt
streamlit run app/ui/app.py
```

## Deploy – Opção 1: Streamlit Community Cloud
1. Suba este repositório para o GitHub.
2. No Streamlit Cloud, crie um novo app apontando para `app/ui/app.py`.
3. Garanta que **requirements.txt** e **packages.txt** estão no repositório.
4. (Opcional) Configure segredos em **Streamlit Cloud → Secrets** (replicam `.streamlit/secrets.toml`).

## Deploy – Opção 2: Hugging Face Spaces (com GPU)
1. Crie um **Space** (SDK: *streamlit*).
2. Suba todo o repositório e inclua o `spaces.yaml` com `hardware: t4-small`.
3. Ative GPU nas configurações do Space.
4. O app roda em `app/ui/app.py`.

## Estrutura
```
/app
  /engine        # motor de regras e scoring
  /engine/rules  # editais parametrizados (YAML)
  /analyzers     # utilitários para pitch PDF e áudio
  /ui            # app Streamlit
/assets          # ícones ou exemplos
/.streamlit      # secrets.toml (não comitar segredos reais)
requirements.txt
packages.txt
spaces.yaml      # para Hugging Face Spaces (opcional)
```

## Avisos
- Transcrição de áudio usa **faster-whisper** e requer **ffmpeg** instalado (via `packages.txt` no Streamlit Cloud).
- Leitura de PDF usa **PyMuPDF**.
- O módulo de valuation é educacional e não substitui parecer financeiro profissional.
