import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import { cores } from '../tema';

export default function RootLayout() {
  return (
    <>
      <StatusBar style="light" />
      <Stack screenOptions={{ headerShown: false, contentStyle: { backgroundColor: cores.fundo }, animation: 'slide_from_right' }} />
    </>
  );
}
