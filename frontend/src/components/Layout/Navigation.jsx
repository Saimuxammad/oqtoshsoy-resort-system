import React, { useState, useEffect } from 'react';
import { useLanguage } from '../../contexts/LanguageContext';
import clsx from 'clsx';
import {
  HomeIcon,
  CalendarDaysIcon,
  ClipboardDocumentListIcon,
  ChartBarIcon,
  ClockIcon,
  Cog6ToothIcon
} from '@heroicons/react/24/outline';

const tabs = [
  { id: 'rooms', icon: HomeIcon, label: 'rooms' },
  { id: 'bookings', icon: ClipboardDocumentListIcon, label: 'bookings' },
  { id: 'calendar', icon: CalendarDaysIcon, label: 'calendar' },
  { id: 'analytics', icon: ChartBarIcon, label: 'analytics' },
  { id: 'history', icon: ClockIcon, label: 'history' },
  { id: 'settings', icon: Cog6ToothIcon, label: 'settings' }
];

export function Navigation({ activeTab, onChange }) {
  const { t } = useLanguage();
  const [activeColor, setActiveColor] = useState('#3b82f6');

  useEffect(() => {
    // Получаем сохраненную тему
    const savedTheme = localStorage.getItem('selectedTheme');
    if (savedTheme) {
      try {
        const theme = JSON.parse(savedTheme);
        setActiveColor(theme.header || '#3b82f6');
      } catch (e) {
        console.error('Error parsing saved theme:', e);
      }
    }

    // Слушаем изменения темы
    const handleThemeChange = (event) => {
      if (event.key === 'selectedTheme' && event.newValue) {
        try {
          const theme = JSON.parse(event.newValue);
          setActiveColor(theme.header || '#3b82f6');
        } catch (e) {
          console.error('Error parsing theme:', e);
        }
      }
    };

    window.addEventListener('storage', handleThemeChange);
    return () => window.removeEventListener('storage', handleThemeChange);
  }, []);

  return (
    <nav className="bg-white border-b border-gray-200 sticky top-0 z-10">
      <div className="container mx-auto">
        <div className="flex overflow-x-auto scrollbar-hide">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;

            return (
              <button
                key={tab.id}
                onClick={() => onChange(tab.id)}
                className={clsx(
                  'flex items-center gap-2 px-4 py-3 border-b-2 transition-all whitespace-nowrap',
                  isActive
                    ? 'border-current text-current font-medium'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                )}
                style={isActive ? { color: activeColor, borderColor: activeColor } : {}}
              >
                <Icon className="h-5 w-5" />
                <span className="text-sm">{t(tab.label)}</span>
              </button>
            );
          })}
        </div>
      </div>
    </nav>
  );
}