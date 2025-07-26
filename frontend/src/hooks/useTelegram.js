import { useEffect, useState } from 'react';

export function useTelegram() {
  const [webApp, setWebApp] = useState(null);
  const [user, setUser] = useState(null);

  useEffect(() => {
    const tg = window.Telegram?.WebApp;

    if (tg) {
      tg.ready();
      tg.expand();

      setWebApp(tg);
      setUser(tg.initDataUnsafe?.user);

      // Set theme
      tg.setHeaderColor('#1e40af');
      tg.setBackgroundColor('#f3f4f6');
    }
  }, []);

  const close = () => {
    webApp?.close();
  };

  const showAlert = (message) => {
    webApp?.showAlert(message);
  };

  const showConfirm = (message) => {
    return new Promise((resolve) => {
      webApp?.showConfirm(message, (confirmed) => {
        resolve(confirmed);
      });
    });
  };

  return {
    webApp,
    user,
    close,
    showAlert,
    showConfirm,
    isReady: !!webApp
  };
}