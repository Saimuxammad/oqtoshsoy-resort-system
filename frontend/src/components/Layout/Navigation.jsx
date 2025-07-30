import React from 'react';
import clsx from 'clsx';
import { useLanguage } from '../../contexts/LanguageContext';
import {
  HomeIcon,
  ClipboardDocumentListIcon,
  CalendarDaysIcon,
  ChartBarIcon,
  ClockIcon,
  Cog6ToothIcon
} from '@heroicons/react/24/outline';

export function Navigation({ activeTab, onChange }) {
  const { t } = useLanguage();

  const tabs = [
    { id: 'rooms', label: 'Xonalar', icon: HomeIcon },
    { id: 'bookings', label: 'Bronlar', icon: ClipboardDocumentListIcon },
    { id: 'calendar', label: 'Kalendar', icon: CalendarDaysIcon },
    { id: 'analytics', label: 'Tahlil', icon: ChartBarIcon },
    { id: 'history', label: 'Tarix', icon: ClockIcon },
    { id: 'settings', label: 'Sozlamalar', icon: Cog6ToothIcon }
  ];

  return (
    <nav className="bg-white border-b border-gray-200">
      <div className="container mx-auto px-4">
        <div className="flex space-x-8 overflow-x-auto">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => onChange(tab.id)}
                className={clsx(
                  'flex items-center gap-2 px-1 py-4 border-b-2 text-sm font-medium transition-colors whitespace-nowrap',
                  activeTab === tab.id
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                )}
              >
                <Icon className="h-5 w-5" />
                {tab.label}
              </button>
            );
          })}
        </div>
      </div>
    </nav>
  );
}