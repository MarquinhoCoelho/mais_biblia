# Mais Bíblia

Histórias da Bíblia em vídeos curtos (formato Shorts), livro por livro, com o texto bíblico, o contexto histórico e a teologia separados em cada vídeo.

```
app/    App Expo (React Native): escolhe o livro e rola os vídeos
api/    API Node + Express em Docker: lista livros/vídeos, serve os MP4 e recebe vídeos novos
video/  Gerador dos vídeos (Python): roteiro -> voz (Kokoro) -> desenhos (SVG) -> MP4
```

## API (Docker)

```bash
cd api
cp .env.example .env      # troque ADMIN_TOKEN (openssl rand -hex 24) e ajuste PUBLIC_URL
docker compose up -d --build
curl http://localhost:3070/saude
```

Os vídeos e o `catalogo.json` ficam em `api/data/` (volume). Faça backup dessa pasta.

| Rota | O que faz |
|---|---|
| `GET /api/livros` | 66 livros com a quantidade de vídeos de cada um |
| `GET /api/videos?livro=mt` | vídeos do livro, em ordem de capítulo e parte |
| `GET /media/<arquivo>` | MP4 e capas (aceita Range) |
| `POST /api/videos` | (token) envia/atualiza vídeo: campos `meta` (JSON), `video`, `capa` |
| `DELETE /api/videos/:id` | (token) apaga |

### Na VPS (produção)

Rodando em `https://senai.vivitsolucoes.com.br/mais-biblia/` (nginx `senai.conf`, bloco `location /mais-biblia/` → `127.0.0.1:3070`).

```bash
cd /opt/mais_biblia && git pull
cd api && docker compose up -d --build     # .env: ADMIN_TOKEN, PORTA=127.0.0.1:3070, PUBLIC_URL=https://senai.vivitsolucoes.com.br/mais-biblia
```

A porta 3070 fica só em localhost; o acesso público passa pelo nginx (HTTPS).

## Vídeo novo (sem gerar APK novo)

```bash
cd video
python falar.py videos/mt02a --vel 1.08
python render.py videos/mt02a
python publicar.py videos/mt02a     # usa MAIS_BIBLIA_API e MAIS_BIBLIA_TOKEN de video/.env
```

O vídeo aparece no app na hora. Os JSON da Bíblia (`nvi.json`, `acf.json`, `aa.json`) ficam fora do repositório, na pasta acima dele (ou em `video/biblia/`).

## App

```bash
cd app
npm install
EXPO_PUBLIC_API_URL=http://localhost:3070 npx expo start
npx eas-cli@latest build -p android --profile preview    # APK
```

A URL da API do APK está em `app/app.json` → `expo.extra.apiUrl`.
