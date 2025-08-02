import { useEffect, useState } from 'react';

export function useTelegram() {
  const [isReady, setIsReady] = useState(false);
  const [user, setUser] = useState(null);

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

      // Устанавливаем цвет заголовка
      if (tg.setHeaderColor) {
        tg.setHeaderColor('#3b82f6');
      }

      // Устанавливаем цвет фона
      if (tg.setBackgroundColor) {
        tg.setBackgroundColor('#f3f4f6');
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
    close
  };
}