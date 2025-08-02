import { useEffect, useState } from 'react';

export function useTelegram() {
  const [isReady, setIsReady] = useState(false);
  const [user, setUser] = useState(null);
  const [colorScheme, setColorScheme] = useState('light');

  useEffect(() => {
    const tg = window.Telegram?.WebApp;

    if (!tg) {
      console.log('[Telegram] Not in Telegram WebApp environment');
      // В браузере устанавливаем тестового пользователя
      setUser({
        id: 123456,
        first_name: 'Test',
        last_name: 'User',
        username: 'testuser'
      });
      setIsReady(true);
      return;
    }

    // Инициализация Telegram WebApp
    try {
      // Расширяем на весь экран
      tg.expand();

      // Включаем кнопку закрытия
      tg.enableClosingConfirmation();

      // Устанавливаем цветовую схему
      const scheme = tg.colorScheme || 'light';
      setColorScheme(scheme);

      // Устанавливаем цвета в соответствии с темой
      if (scheme === 'dark') {
        // Темная тема
        if (tg.setHeaderColor) {
          tg.setHeaderColor('#1e293b'); // Темно-синий
        }
        if (tg.setBackgroundColor) {
          tg.setBackgroundColor('#0f172a'); // Еще темнее
        }
      } else {
        // Светлая тема - ваш синий цвет
        if (tg.setHeaderColor) {
          tg.setHeaderColor('#3b82f6'); // Синий как на скриншоте
        }
        if (tg.setBackgroundColor) {
          tg.setBackgroundColor('#ffffff'); // Белый фон
        }
      }

      // Дополнительно устанавливаем цвет нижней панели
      if (tg.setBottomBarColor) {
        tg.setBottomBarColor('#3b82f6'); // Такой же как заголовок
      }

      // Получаем данные пользователя
      const userData = tg.initDataUnsafe?.user;
      if (userData) {
        setUser(userData);
      }

      setIsReady(true);

      // Показываем, что приложение готово
      tg.ready();
    } catch (error) {
      console.error('[Telegram] Initialization error:', error);
      setIsReady(true);
    }
  }, []);

  const showAlert = (message) => {
    const tg = window.Telegram?.WebApp;
    if (tg && tg.showAlert) {
      tg.showAlert(message);
    } else {
      alert(message);
    }
  };

  const showConfirm = (message, callback) => {
    const tg = window.Telegram?.WebApp;
    if (tg && tg.showConfirm) {
      tg.showConfirm(message, callback);
    } else {
      const result = confirm(message);
      callback(result);
    }
  };

  const close = () => {
    const tg = window.Telegram?.WebApp;
    if (tg && tg.close) {
      tg.close();
    }
  };

  return {
    tg: window.Telegram?.WebApp,
    user,
    isReady,
    showAlert,
    showConfirm,
    close,
    colorScheme,
    setHeaderColor: (color) => {
      const tg = window.Telegram?.WebApp;
      if (tg && tg.setHeaderColor) {
        tg.setHeaderColor(color);
      }
    },
    setBackgroundColor: (color) => {
      const tg = window.Telegram?.WebApp;
      if (tg && tg.setBackgroundColor) {
        tg.setBackgroundColor(color);
      }
    }
  };
}