import { useEvent, useEventListener } from 'expo';
import { Image } from 'expo-image';
import { useVideoPlayer, VideoView } from 'expo-video';
import { useEffect, useState } from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';
import { Video } from '../lib/api';
import { cores } from '../tema';

type Props = { video: Video; altura: number; ativo: boolean; perto: boolean; baixo: number };

/** Um short em tela cheia. Só monta o player quando está na tela ou ao lado (economiza memória). */
export function Short({ video, altura, ativo, perto, baixo }: Props) {
  const [info, setInfo] = useState(false);
  return (
    <View style={[s.caixa, { height: altura }]}>
      {perto ? (
        <Player url={video.url} ativo={ativo} />
      ) : video.capa ? (
        <Image source={video.capa} style={StyleSheet.absoluteFill} contentFit="cover" />
      ) : null}

      <View style={[s.rodape, { paddingBottom: baixo + 18 }]} pointerEvents="box-none">
        <View style={s.etiqueta}>
          <Text style={s.etiquetaTxt}>
            {video.trecho || `Capítulo ${video.capitulo}`}
            {video.parte > 1 ? `  ·  parte ${video.parte}` : ''}
          </Text>
        </View>
        <Text style={s.titulo}>{video.titulo}</Text>
        <Pressable onPress={() => setInfo((v) => !v)} hitSlop={8} accessibilityRole="button" accessibilityLabel="Ver versículos e fontes">
          <Text style={s.mais}>{info ? 'Ocultar fontes ▴' : 'Versículos e fontes ▾'}</Text>
        </Pressable>
        {info && (
          <View style={s.fontes}>
            {video.descricao ? <Text style={s.fonteTxt}>{video.descricao}</Text> : null}
            {video.fontes.map((f) => (
              <Text key={f} style={s.fonteTxt}>
                • {f}
              </Text>
            ))}
            <Text style={s.aviso}>Partes marcadas como “dado histórico” vêm de fontes fora da Bíblia. Voz gerada por IA.</Text>
          </View>
        )}
      </View>
    </View>
  );
}

function Player({ url, ativo }: { url: string; ativo: boolean }) {
  const player = useVideoPlayer(url, (p) => {
    p.loop = true;
    p.timeUpdateEventInterval = 0.25;
  });
  const { isPlaying } = useEvent(player, 'playingChange', { isPlaying: player.playing });
  const [prog, setProg] = useState(0);
  useEventListener(player, 'timeUpdate', (e) => {
    if (player.duration > 0) setProg(e.currentTime / player.duration);
  });
  useEffect(() => {
    if (ativo) {
      player.play();
    } else {
      player.pause();
      player.seekBy(-player.currentTime);
    }
  }, [ativo, player]);

  return (
    <View style={StyleSheet.absoluteFill}>
      <VideoView player={player} style={s.video} contentFit="contain" nativeControls={false} />
      <Pressable
        style={StyleSheet.absoluteFill}
        onPress={() => (player.playing ? player.pause() : player.play())}
        accessibilityRole="button"
        accessibilityLabel={isPlaying ? 'Pausar' : 'Tocar'}
      >
        {!isPlaying && ativo && (
          <View style={s.pausa} pointerEvents="none">
            <Text style={s.pausaTxt}>▶</Text>
          </View>
        )}
      </Pressable>
      <View style={s.barra} pointerEvents="none">
        <View style={[s.barraCheia, { width: `${Math.min(100, prog * 100)}%` }]} />
      </View>
    </View>
  );
}

const s = StyleSheet.create({
  caixa: { width: '100%', backgroundColor: '#000', justifyContent: 'flex-end' },
  video: { position: 'absolute', top: 0, left: 0, width: '100%', height: '100%' },
  rodape: { paddingHorizontal: 16, gap: 6, backgroundColor: 'rgba(0,0,0,0.55)', paddingTop: 14 },
  etiqueta: { alignSelf: 'flex-start', backgroundColor: cores.papel, borderRadius: 8, paddingHorizontal: 10, paddingVertical: 4 },
  etiquetaTxt: { color: cores.azul, fontWeight: '800', fontSize: 14 },
  titulo: { color: '#fff', fontSize: 18, fontWeight: '800' },
  mais: { color: '#e9a69f', fontWeight: '700', fontSize: 14, paddingVertical: 2 },
  fontes: { gap: 4 },
  fonteTxt: { color: '#eee', fontSize: 13, lineHeight: 18 },
  aviso: { color: '#bbb', fontSize: 12, fontStyle: 'italic', marginTop: 4 },
  pausa: { position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, alignItems: 'center', justifyContent: 'center' },
  pausaTxt: { color: 'rgba(255,255,255,0.85)', fontSize: 72 },
  barra: { position: 'absolute', left: 0, right: 0, bottom: 0, height: 3, backgroundColor: 'rgba(255,255,255,0.25)' },
  barraCheia: { height: 3, backgroundColor: cores.vermelho },
});
