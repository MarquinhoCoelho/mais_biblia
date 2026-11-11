import Constants from 'expo-constants';

// EXPO_PUBLIC_API_URL troca a API em desenvolvimento (ex.: http://localhost:3070)
export const API_URL: string =
  process.env.EXPO_PUBLIC_API_URL || ((Constants.expoConfig?.extra?.apiUrl as string) ?? 'http://92.112.176.96:3070');

export type Livro = {
  abrev: string;
  nome: string;
  testamento: 'AT' | 'NT';
  ordem: number;
  capitulos: number;
  videos: number;
};

export type Video = {
  id: string;
  livro: string;
  capitulo: number;
  versiculos: string;
  parte: number;
  titulo: string;
  trecho: string;
  descricao: string;
  fontes: string[];
  duracao: number | null;
  url: string;
  capa: string | null;
};

async function get<T>(caminho: string): Promise<T> {
  const ctrl = new AbortController();
  const t = setTimeout(() => ctrl.abort(), 15000);
  try {
    const r = await fetch(`${API_URL}${caminho}`, { signal: ctrl.signal });
    if (!r.ok) throw new Error(`Erro ${r.status}`);
    return (await r.json()) as T;
  } finally {
    clearTimeout(t);
  }
}

export const buscarLivros = () => get<Livro[]>('/api/livros');
export const buscarVideos = (livro: string) => get<Video[]>(`/api/videos?livro=${encodeURIComponent(livro)}`);
