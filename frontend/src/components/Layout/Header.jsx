import React, { useState, useEffect } from 'react';
import { useLanguage } from '../../contexts/LanguageContext';

export function Header() {
  const { t } = useLanguage();
  const [headerColor, setHeaderColor] = useState('#3b82f6');

  useEffect(() => {
    // Получаем сохраненную тему
    const savedTheme = localStorage.getItem('selectedTheme');
    if (savedTheme) {
      try {
        const theme = JSON.parse(savedTheme);
        setHeaderColor(theme.header || '#3b82f6');
      } catch (e) {
        console.error('Error parsing saved theme:', e);
      }
    }

    // Слушаем изменения темы
    const handleThemeChange = (event) => {
      if (event.key === 'selectedTheme' && event.newValue) {
        try {
          const theme = JSON.parse(event.newValue);
          setHeaderColor(theme.header || '#3b82f6');
        } catch (e) {
          console.error('Error parsing theme:', e);
        }
      }
    };

    window.addEventListener('storage', handleThemeChange);
    return () => window.removeEventListener('storage', handleThemeChange);
  }, []);

  return (
    <header
      className="text-white p-4 shadow-lg"
      style={{ backgroundColor: headerColor }}
    >
      <div className="container mx-auto">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center">
              <span className="text-xl font-bold">O</span>
            </div>
            <div>
              <h1 className="text-xl font-bold">Oqtoshsoy Resort</h1>
              <p className="text-sm opacity-90">Xonalarni boshqarish tizimi</p>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}