import type { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.rougcorp.swingandsnap',   // ← REMPLACEZ par votre bundle ID
  appName: 'Swing & Snap',
  webDir: 'www',
  server: {
    androidScheme: 'https'
  },
  plugins: {
    SplashScreen: {
      launchShowDuration: 800,
      backgroundColor: '#F5F0E8',
      showSpinner: false,
      launchAutoHide: true
    },
    StatusBar: {
      style: 'LIGHT',
      backgroundColor: '#F5F0E8'
    }
  }
};

export default config;
