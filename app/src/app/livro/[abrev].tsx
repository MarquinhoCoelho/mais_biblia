import { router, useLocalSearchParams } from 'expo-router';
import { useCallback, useEffect, useState } from 'react';
import { ActivityIndicator, FlatList, Pressable, StyleSheet, Text, View } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { SeletorLivro } from '../../componentes/SeletorLivro';
import { Short } from '../../componentes/Short';
import { buscarLivros, buscarVideos, Livro, Video } from '../../lib/api';
import { cores } from '../../tema';

/** Feed vertical de shorts de um livro, em ordem de capítulo e parte. */
export default function FeedLivro() {
  const { abrev, nome } = useLocalSearchParams<{ abrev: string; nome?: string }>();
  const ins = useSafeAreaInsets();
  const [estado, setEstado] = useState<{ abrev: string; videos: Video[] | null; erro: boolean } | null>(null);
  const [tentativa, setTentativa] = useState(0);
  const videos = estado?.abrev === abrev ? estado.videos : null;
  const erro = estado?.abrev === abrev ? estado.erro : false;
  const [ativo, setAtivo] = useState(0);
  const [altura, setAltura] = useState(0);
  const [livros, setLivros] = useState<Livro[]>([]);
  const [seletor, setSeletor] = useState(false);

  useEffect(() => {
    let vivo = true;
    buscarVideos(abrev)
      .then((v) => {
        if (!vivo) return;
        setAtivo(0);
        setEstado({ abrev, videos: v, erro: false });
      })
      .catch(() => vivo && setEstado({ abrev, videos: null, erro: true }));
    return () => {
      vivo = false;
    };
  }, [abrev, tentativa]);
  useEffect(() => {
    buscarLivros().then(setLivros).catch(() => {});
  }, []);
  const carregar = () => {
    setEstado(null);
    setTentativa((t) => t + 1);
  };

  const aoVer = useCallback(({ viewableItems }: { viewableItems: { index?: number | null; isViewable: boolean }[] }) => {
    const v = viewableItems.find((x) => x.isViewable);
    if (v?.index != null) setAtivo(v.index);
  }, []);

  const trocarLivro = (l: Livro) => {
    setSeletor(false);
    if (l.abrev !== abrev) router.setParams({ abrev: l.abrev, nome: l.nome });
  };

  return (
    <View style={s.tela} onLayout={(e) => setAltura(e.nativeEvent.layout.height)}>
      {videos && altura > 0 && videos.length > 0 && (
        <FlatList
          data={videos}
          keyExtractor={(v) => v.id}
          renderItem={({ item, index }) => (
            <Short video={item} altura={altura} ativo={index === ativo} perto={Math.abs(index - ativo) <= 1} baixo={ins.bottom} />
          )}
          pagingEnabled
          snapToInterval={altura}
          decelerationRate="fast"
          showsVerticalScrollIndicator={false}
          getItemLayout={(_, i) => ({ length: altura, offset: altura * i, index: i })}
          onViewableItemsChanged={aoVer}
          viewabilityConfig={{ itemVisiblePercentThreshold: 60 }}
          windowSize={3}
          initialNumToRender={1}
          maxToRenderPerBatch={2}
        />
      )}

      {!videos && !erro && <ActivityIndicator color={cores.papel} style={s.centro} />}
      {erro && (
        <View style={s.centro}>
          <Text style={s.msg}>Não foi possível carregar os vídeos.</Text>
          <Pressable onPress={carregar} style={s.botao} accessibilityRole="button">
            <Text style={s.botaoTxt}>Tentar de novo</Text>
          </Pressable>
        </View>
      )}
      {videos && videos.length === 0 && (
        <View style={s.centro}>
          <Text style={s.msg}>Ainda não há vídeos de {nome ?? 'este livro'}.</Text>
          <Text style={s.msgPeq}>Escolha outro livro no menu acima.</Text>
        </View>
      )}

      <View style={[s.topo, { paddingTop: ins.top + 8 }]} pointerEvents="box-none">
        <Pressable onPress={() => router.back()} style={s.voltar} hitSlop={10} accessibilityRole="button" accessibilityLabel="Voltar">
          <Text style={s.voltarTxt}>‹</Text>
        </Pressable>
        <Pressable
          onPress={() => setSeletor(true)}
          style={s.livroBtn}
          accessibilityRole="button"
          accessibilityLabel={`Livro atual: ${nome}. Trocar livro`}
        >
          <Text style={s.livroTxt}>{nome ?? abrev}</Text>
          <Text style={s.livroSeta}>▾</Text>
        </Pressable>
        {videos && videos.length > 0 && (
          <Text style={s.contador}>
            {ativo + 1}/{videos.length}
          </Text>
        )}
      </View>

      <SeletorLivro aberto={seletor} livros={livros} atual={abrev} fechar={() => setSeletor(false)} escolher={trocarLivro} />
    </View>
  );
}

const s = StyleSheet.create({
  tela: { flex: 1, backgroundColor: '#000' },
  centro: { position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, alignItems: 'center', justifyContent: 'center', padding: 24, gap: 10 },
  msg: { color: cores.papel, fontSize: 17, fontWeight: '700', textAlign: 'center' },
  msgPeq: { color: cores.apagado, textAlign: 'center' },
  botao: { backgroundColor: cores.vermelho, paddingVertical: 12, paddingHorizontal: 20, borderRadius: 12 },
  botaoTxt: { color: '#fff', fontWeight: '800' },
  topo: { position: 'absolute', top: 0, left: 0, right: 0, flexDirection: 'row', alignItems: 'center', gap: 10, paddingHorizontal: 12 },
  voltar: { width: 40, height: 40, borderRadius: 20, backgroundColor: 'rgba(0,0,0,0.5)', alignItems: 'center', justifyContent: 'center' },
  voltarTxt: { color: '#fff', fontSize: 30, lineHeight: 32, marginTop: -2 },
  livroBtn: { flexDirection: 'row', alignItems: 'center', gap: 6, backgroundColor: 'rgba(0,0,0,0.55)', paddingHorizontal: 14, paddingVertical: 9, borderRadius: 20 },
  livroTxt: { color: '#fff', fontWeight: '800', fontSize: 16 },
  livroSeta: { color: '#fff', fontSize: 14 },
  contador: { marginLeft: 'auto', color: '#fff', fontWeight: '700', backgroundColor: 'rgba(0,0,0,0.5)', paddingHorizontal: 10, paddingVertical: 6, borderRadius: 12 },
});
