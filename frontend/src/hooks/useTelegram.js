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
      // В новых версиях Telegram WebApp API используется themeParams
      if (tg.themeParams) {
        console.log('[Telegram] Theme params:', tg.themeParams);
      }

      // Пробуем разные методы установки цвета
      try {
        // Метод 1: setHeaderColor (старый API)
        if (tg.setHeaderColor) {
          tg.setHeaderColor(scheme === 'dark' ? '#1e293b' : '#3b82f6');
        }

        // Метод 2: через CSS переменные
        if (tg.headerColor !== undefined) {
          tg.headerColor = scheme === 'dark' ? '#1e293b' : '#3b82f6';
        }

        // Метод 3: через тему
        if (tg.setThemeParams) {
          tg.setThemeParams({
            bg_color: '#ffffff',
            header_bg_color: scheme === 'dark' ? '#1e293b' : '#3b82f6',
            text_color: '#000000',
            hint_color: '#999999',
            link_color: '#3b82f6',
            button_color: '#3b82f6',
            button_text_color: '#ffffff'
          });
        }
      } catch (error) {
        console.error('[Telegram] Error setting colors:', error);
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
      if (!tg) return;

      console.log('[Telegram] Setting header color to:', color);

      // Пробуем все возможные методы
      try {
        // Метод 1
        if (tg.setHeaderColor) {
          tg.setHeaderColor(color);
        }

        // Метод 2
        if (tg.headerColor !== undefined) {
          tg.headerColor = color;
        }

        // Метод 3 - через параметры темы
        if (tg.setThemeParams) {
          tg.setThemeParams({
            header_bg_color: color
          });
        }

        // Метод 4 - через MainButton для теста
        if (tg.MainButton) {
          tg.MainButton.color = color;
        }
      } catch (error) {
        console.error('[Telegram] Error in setHeaderColor:', error);
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