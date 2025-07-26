import { useEffect, useState } from 'react';

export function useTelegram() {
  const [webApp, setWebApp] = useState(null);
  const [user, setUser] = useState(null);

  useEffect(() => {
    console.log('Telegram WebApp:', window.Telegram?.WebApp);
    const tg = window.Telegram?.WebApp;

    if (tg && tg.initData) {
      console.log('Telegram WebApp found');
      tg.ready();
      tg.expand();

      setWebApp(tg);
      setUser(tg.initDataUnsafe?.user);

      // Set theme - с проверкой на существование методов
      if (tg.setHeaderColor) {
        tg.setHeaderColor('#1e40af');
      }
      if (tg.setBackgroundColor) {
        tg.setBackgroundColor('#f3f4f6');
      }
    } else {
      // Development mode - если нет Telegram WebApp
      console.warn('Telegram WebApp not found, using development mode');
      setWebApp({
        ready: () => {},
        expand: () => {},
        close: () => {},
        showAlert: (message) => alert(message),
        showConfirm: (message, callback) => {
          const result = confirm(message);
          if (callback) callback(result);
        }
      });
      setUser({
        id: 123456789,
        first_name: 'Test',
        last_name: 'User',
        username: 'testuser'
      });
    }
  }, []);

  const close = () => {
    webApp?.close?.();
  };

  const showAlert = (message) => {
    if (webApp?.showAlert) {
      webApp.showAlert(message);
    } else {
      alert(message);
    }
  };

  const showConfirm = (message) => {
    return new Promise((resolve) => {
      if (webApp?.showConfirm) {
        webApp.showConfirm(message, (confirmed) => {
          resolve(confirmed);
        });
      } else {
        resolve(confirm(message));
      }
    });
  };

  return {
    webApp,
    user,
    close,
    showAlert,
    showConfirm,
    isReady: true // Всегда готов
  };
}