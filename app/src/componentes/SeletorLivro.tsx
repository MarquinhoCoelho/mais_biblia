import { Modal, Pressable, SectionList, StyleSheet, Text, View } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { Livro } from '../lib/api';
import { cores } from '../tema';

type Props = {
  aberto: boolean;
  livros: Livro[];
  atual?: string;
  fechar: () => void;
  escolher: (l: Livro) => void;
};

/** Lista de todos os livros (Antigo e Novo Testamento) em um modal, como um "select". */
export function SeletorLivro({ aberto, livros, atual, fechar, escolher }: Props) {
  const ins = useSafeAreaInsets();
  const secoes = [
    { title: 'Novo Testamento', data: livros.filter((l) => l.testamento === 'NT') },
    { title: 'Antigo Testamento', data: livros.filter((l) => l.testamento === 'AT') },
  ];
  return (
    <Modal visible={aberto} animationType="slide" onRequestClose={fechar} transparent>
      <View style={s.fundo}>
        <View style={[s.folha, { paddingBottom: ins.bottom + 12 }]}>
          <View style={s.topo}>
            <Text style={s.titulo}>Escolha o livro</Text>
            <Pressable onPress={fechar} hitSlop={12} accessibilityRole="button" accessibilityLabel="Fechar">
              <Text style={s.fechar}>✕</Text>
            </Pressable>
          </View>
          <SectionList
            sections={secoes}
            keyExtractor={(l) => l.abrev}
            stickySectionHeadersEnabled
            renderSectionHeader={({ section }) => <Text style={s.secao}>{section.title}</Text>}
            renderItem={({ item }) => {
              const tem = item.videos > 0;
              const sel = item.abrev === atual;
              return (
                <Pressable
                  onPress={() => escolher(item)}
                  style={({ pressed }) => [s.linha, sel && s.linhaSel, pressed && { opacity: 0.6 }]}
                  accessibilityRole="button"
                  accessibilityLabel={`${item.nome}, ${tem ? `${item.videos} vídeos` : 'em breve'}`}
                >
                  <Text style={[s.nome, !tem && s.apagado]}>{item.nome}</Text>
                  <Text style={[s.qtd, tem ? s.qtdTem : s.apagado]}>
                    {tem ? `${item.videos} ${item.videos === 1 ? 'vídeo' : 'vídeos'}` : 'em breve'}
                  </Text>
                </Pressable>
              );
            }}
          />
        </View>
      </View>
    </Modal>
  );
}

const s = StyleSheet.create({
  fundo: { flex: 1, backgroundColor: 'rgba(0,0,0,0.6)', justifyContent: 'flex-end' },
  folha: { backgroundColor: cores.papel, borderTopLeftRadius: 24, borderTopRightRadius: 24, maxHeight: '85%', paddingHorizontal: 16 },
  topo: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingVertical: 16 },
  titulo: { fontSize: 22, fontWeight: '800', color: cores.tinta },
  fechar: { fontSize: 22, color: cores.tinta, paddingHorizontal: 4 },
  secao: { backgroundColor: cores.papel, color: cores.vermelho, fontWeight: '800', fontSize: 13, letterSpacing: 1, textTransform: 'uppercase', paddingTop: 14, paddingBottom: 6 },
  linha: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', paddingVertical: 13, paddingHorizontal: 10, borderBottomWidth: 1, borderBottomColor: cores.linha, borderRadius: 8 },
  linhaSel: { backgroundColor: '#f1e6c9' },
  nome: { fontSize: 17, color: cores.tinta, fontWeight: '600' },
  qtd: { fontSize: 13, fontWeight: '700' },
  qtdTem: { color: cores.azul },
  apagado: { color: cores.apagado },
});
