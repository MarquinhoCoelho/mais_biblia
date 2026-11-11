import { router } from 'expo-router';
import { useCallback, useEffect, useState } from 'react';
import { ActivityIndicator, Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { SeletorLivro } from '../componentes/SeletorLivro';
import { buscarLivros, Livro } from '../lib/api';
import { cores } from '../tema';

export default function Inicio() {
  const ins = useSafeAreaInsets();
  const [livros, setLivros] = useState<Livro[] | null>(null);
  const [erro, setErro] = useState(false);
  const [aberto, setAberto] = useState(false);

  const buscar = useCallback(() => {
    buscarLivros()
      .then((l) => {
        setErro(false);
        setLivros(l);
      })
      .catch(() => setErro(true));
  }, []);
  useEffect(buscar, [buscar]);
  const carregar = () => {
    setErro(false);
    buscar();
  };

  const abrir = (l: Livro) => {
    setAberto(false);
    router.push({ pathname: '/livro/[abrev]', params: { abrev: l.abrev, nome: l.nome } });
  };
  const comVideos = (livros ?? []).filter((l) => l.videos > 0);

  return (
    <View style={[s.tela, { paddingTop: ins.top + 24 }]}>
      <Text style={s.marca}>Mais Bíblia</Text>
      <Text style={s.sub}>Histórias da Bíblia em vídeos curtos, com o contexto histórico de cada trecho.</Text>

      <Pressable
        style={({ pressed }) => [s.select, pressed && { opacity: 0.8 }]}
        onPress={() => setAberto(true)}
        disabled={!livros}
        accessibilityRole="button"
        accessibilityLabel="Escolher livro da Bíblia"
      >
        <Text style={s.selectTxt}>Escolha um livro</Text>
        <Text style={s.selectSeta}>▾</Text>
      </Pressable>

      {!livros && !erro && <ActivityIndicator color={cores.papel} style={{ marginTop: 32 }} />}
      {erro && (
        <View style={s.erro}>
          <Text style={s.erroTxt}>Não foi possível carregar. Verifique sua internet.</Text>
          <Pressable onPress={carregar} style={s.botao} accessibilityRole="button">
            <Text style={s.botaoTxt}>Tentar de novo</Text>
          </Pressable>
        </View>
      )}

      {livros && (
        <ScrollView contentContainerStyle={{ paddingBottom: ins.bottom + 24 }}>
          <Text style={s.secao}>Livros com vídeos</Text>
          {comVideos.length === 0 && <Text style={s.vazio}>Os primeiros vídeos estão chegando.</Text>}
          <View style={s.grade}>
            {comVideos.map((l) => (
              <Pressable
                key={l.abrev}
                onPress={() => abrir(l)}
                style={({ pressed }) => [s.cartao, pressed && { opacity: 0.7 }]}
                accessibilityRole="button"
                accessibilityLabel={`${l.nome}, ${l.videos} vídeos`}
              >
                <Text style={s.cartaoNome}>{l.nome}</Text>
                <Text style={s.cartaoQtd}>
                  {l.videos} {l.videos === 1 ? 'vídeo' : 'vídeos'}
                </Text>
              </Pressable>
            ))}
          </View>
        </ScrollView>
      )}

      <SeletorLivro aberto={aberto} livros={livros ?? []} fechar={() => setAberto(false)} escolher={abrir} />
    </View>
  );
}

const s = StyleSheet.create({
  tela: { flex: 1, backgroundColor: cores.fundo, paddingHorizontal: 16 },
  marca: { color: cores.papel, fontSize: 34, fontWeight: '900' },
  sub: { color: cores.apagado, fontSize: 15, marginTop: 6, lineHeight: 21 },
  select: { marginTop: 24, backgroundColor: cores.papel, borderRadius: 14, paddingVertical: 16, paddingHorizontal: 18, flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  selectTxt: { fontSize: 18, fontWeight: '800', color: cores.tinta },
  selectSeta: { fontSize: 20, color: cores.tinta },
  secao: { color: cores.papel, fontWeight: '800', fontSize: 16, marginTop: 28, marginBottom: 12 },
  vazio: { color: cores.apagado },
  grade: { flexDirection: 'row', flexWrap: 'wrap', gap: 10 },
  cartao: { width: '48%', flexGrow: 1, backgroundColor: cores.cartao, borderColor: cores.borda, borderWidth: 1, borderRadius: 14, padding: 16 },
  cartaoNome: { color: cores.papel, fontSize: 18, fontWeight: '800' },
  cartaoQtd: { color: '#e9a69f', fontSize: 13, marginTop: 4, fontWeight: '700' },
  erro: { marginTop: 32, alignItems: 'center', gap: 12 },
  erroTxt: { color: cores.papel, textAlign: 'center' },
  botao: { backgroundColor: cores.vermelho, paddingVertical: 12, paddingHorizontal: 20, borderRadius: 12 },
  botaoTxt: { color: '#fff', fontWeight: '800' },
});
