// API do Mais Bíblia: lista livros e vídeos, serve os MP4 (com Range, para o player) e recebe vídeos novos.
// Dados em DATA_DIR (volume do Docker): catalogo.json + media/<id>.mp4 + media/<id>.jpg
import express from 'express';
import cors from 'cors';
import multer from 'multer';
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const PORT = Number(process.env.PORT || 3000);
const DATA_DIR = process.env.DATA_DIR || path.join(__dirname, '..', 'data');
const MEDIA_DIR = path.join(DATA_DIR, 'media');
const CATALOGO = path.join(DATA_DIR, 'catalogo.json');
const ADMIN_TOKEN = process.env.ADMIN_TOKEN || '';
const PUBLIC_URL = (process.env.PUBLIC_URL || '').replace(/\/$/, '');
const LIVROS = JSON.parse(fs.readFileSync(path.join(__dirname, 'livros.json'), 'utf-8'));

fs.mkdirSync(MEDIA_DIR, { recursive: true });

function lerCatalogo() {
  try {
    return JSON.parse(fs.readFileSync(CATALOGO, 'utf-8'));
  } catch {
    return [];
  }
}

function salvarCatalogo(lista) {
  const tmp = CATALOGO + '.tmp';
  fs.writeFileSync(tmp, JSON.stringify(lista, null, 1));
  fs.renameSync(tmp, CATALOGO);
}

function base(req) {
  return PUBLIC_URL || `${req.protocol}://${req.get('host')}`;
}

function publico(v, req) {
  const b = base(req);
  return {
    ...v,
    url: `${b}/media/${v.arquivo}`,
    capa: v.capa_arquivo ? `${b}/media/${v.capa_arquivo}` : null,
  };
}

function ordenar(a, b) {
  const la = LIVROS.find((l) => l.abrev === a.livro)?.ordem ?? 999;
  const lb = LIVROS.find((l) => l.abrev === b.livro)?.ordem ?? 999;
  return la - lb || a.capitulo - b.capitulo || (a.parte ?? 1) - (b.parte ?? 1);
}

function exigirAdmin(req, res, next) {
  const tok = (req.get('authorization') || '').replace(/^Bearer\s+/i, '');
  const ok = ADMIN_TOKEN && tok.length === ADMIN_TOKEN.length &&
    crypto.timingSafeEqual(Buffer.from(tok), Buffer.from(ADMIN_TOKEN));
  if (!ok) return res.status(401).json({ erro: 'token inválido' });
  next();
}

const app = express();
app.set('trust proxy', true);
app.use(cors());
app.use(express.json({ limit: '1mb' }));

app.get('/saude', (_req, res) => res.json({ ok: true }));

app.get('/api/livros', (_req, res) => {
  const cat = lerCatalogo();
  res.json(LIVROS.map((l) => ({ ...l, videos: cat.filter((v) => v.livro === l.abrev).length })));
});

app.get('/api/videos', (req, res) => {
  let cat = lerCatalogo();
  if (req.query.livro) cat = cat.filter((v) => v.livro === req.query.livro);
  if (req.query.capitulo) cat = cat.filter((v) => v.capitulo === Number(req.query.capitulo));
  res.set('Cache-Control', 'no-cache');
  res.json(cat.sort(ordenar).map((v) => publico(v, req)));
});

app.get('/api/videos/:id', (req, res) => {
  const v = lerCatalogo().find((x) => x.id === req.params.id);
  if (!v) return res.status(404).json({ erro: 'não encontrado' });
  res.json(publico(v, req));
});

app.use('/media', express.static(MEDIA_DIR, { maxAge: '30d', immutable: true }));

// ---------- admin: subir / apagar vídeos
const upload = multer({
  storage: multer.diskStorage({
    destination: MEDIA_DIR,
    filename: (_req, file, cb) => cb(null, `_up_${Date.now()}_${crypto.randomBytes(4).toString('hex')}${path.extname(file.originalname)}`),
  }),
  limits: { fileSize: 300 * 1024 * 1024 },
});

app.post('/api/videos', exigirAdmin, upload.fields([{ name: 'video', maxCount: 1 }, { name: 'capa', maxCount: 1 }]), (req, res) => {
  const limpar = () => Object.values(req.files || {}).flat().forEach((f) => fs.rmSync(f.path, { force: true }));
  try {
    const meta = JSON.parse(req.body.meta || '{}');
    if (!/^[a-z0-9_-]{2,60}$/.test(meta.id || '')) throw new Error('meta.id inválido (use letras minúsculas, números, - e _)');
    if (!LIVROS.some((l) => l.abrev === meta.livro)) throw new Error('meta.livro inválido');
    if (!Number.isInteger(meta.capitulo)) throw new Error('meta.capitulo deve ser inteiro');
    const video = req.files?.video?.[0];
    const cat = lerCatalogo();
    const antigo = cat.find((v) => v.id === meta.id);
    if (!video && !antigo) throw new Error('falta o arquivo de vídeo');
    const versao = Date.now().toString(36);
    const reg = {
      id: meta.id,
      livro: meta.livro,
      capitulo: meta.capitulo,
      versiculos: String(meta.versiculos || ''),
      parte: meta.parte ?? 1,
      titulo: meta.titulo || '',
      trecho: meta.trecho || '',
      descricao: meta.descricao || '',
      fontes: Array.isArray(meta.fontes) ? meta.fontes : [],
      duracao: meta.duracao ?? null,
      arquivo: antigo?.arquivo,
      capa_arquivo: antigo?.capa_arquivo ?? null,
      atualizado: new Date().toISOString(),
    };
    if (video) {
      reg.arquivo = `${meta.id}-${versao}.mp4`;
      fs.renameSync(video.path, path.join(MEDIA_DIR, reg.arquivo));
      if (antigo?.arquivo) fs.rmSync(path.join(MEDIA_DIR, antigo.arquivo), { force: true });
    }
    const capa = req.files?.capa?.[0];
    if (capa) {
      reg.capa_arquivo = `${meta.id}-${versao}.jpg`;
      fs.renameSync(capa.path, path.join(MEDIA_DIR, reg.capa_arquivo));
      if (antigo?.capa_arquivo) fs.rmSync(path.join(MEDIA_DIR, antigo.capa_arquivo), { force: true });
    }
    salvarCatalogo([...cat.filter((v) => v.id !== meta.id), reg]);
    res.status(antigo ? 200 : 201).json(publico(reg, req));
  } catch (e) {
    limpar();
    res.status(400).json({ erro: e.message });
  }
});

app.delete('/api/videos/:id', exigirAdmin, (req, res) => {
  const cat = lerCatalogo();
  const v = cat.find((x) => x.id === req.params.id);
  if (!v) return res.status(404).json({ erro: 'não encontrado' });
  for (const f of [v.arquivo, v.capa_arquivo]) if (f) fs.rmSync(path.join(MEDIA_DIR, f), { force: true });
  salvarCatalogo(cat.filter((x) => x.id !== v.id));
  res.json({ ok: true });
});

app.listen(PORT, () => console.log(`mais-biblia-api na porta ${PORT}`));
