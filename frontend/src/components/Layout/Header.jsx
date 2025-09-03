import React, { useState, useEffect } from 'react';
import { useLanguage } from '../../contexts/LanguageContext';
import { ArrowRightOnRectangleIcon, UserIcon } from '@heroicons/react/24/outline';

export function Header({ currentUser, onLogout }) {
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

  const getRoleBadgeColor = (role) => {
    const colors = {
      Administrator: 'bg-red-100 text-red-800',
      Manager: 'bg-blue-100 text-blue-800',
      Operator: 'bg-green-100 text-green-800',
      Viewer: 'bg-gray-100 text-gray-800'
    };
    return colors[role] || 'bg-gray-100 text-gray-800';
  };

  return (
    <header
      className="text-white p-4 shadow-lg"
      style={{ backgroundColor: headerColor }}
    >
      <div className="container mx-auto">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            {/* Logo */}
            <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center overflow-hidden">
              <img
                src="/logo.png"
                alt="O"
                className="w-full h-full object-cover"
                onError={(e) => {
                  // Agar logo topilmasa, default harf ko'rsatiladi
                  e.target.style.display = 'none';
                  e.target.parentElement.innerHTML = '<span class="text-xl font-bold">O</span>';
                }}
              />
            </div>

            {/* Tizim nomi */}
            <div>
              <h1 className="text-xl font-bold">Oqtoshsoy Resort</h1>
              <p className="text-sm opacity-90">Xonalarni boshqarish tizimi</p>
            </div>
          </div>

          {/* Foydalanuvchi ma'lumotlari */}
          {currentUser && (
            <div className="flex items-center gap-4">
              <div className="text-right">
                <div className="flex items-center gap-2">
                  <UserIcon className="h-5 w-5" />
                  <span className="font-medium">{currentUser.name}</span>
                </div>
                <span className={`inline-block px-2 py-1 rounded-full text-xs font-medium ${getRoleBadgeColor(currentUser.role)}`}>
                  {currentUser.role}
                </span>
              </div>

              <button
                onClick={onLogout}
                className="flex items-center gap-2 px-3 py-2 bg-white/20 hover:bg-white/30 rounded-lg transition-colors"
                title="Chiqish"
              >
                <ArrowRightOnRectangleIcon className="h-5 w-5" />
                <span className="text-sm">Chiqish</span>
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}