import React from 'react';
import { Card, CardContent } from '../UI/Card';
import { useLanguage } from '../../contexts/LanguageContext';

export function RoomFilter({ filters, onChange }) {
  const { t } = useLanguage();

  const roomTypes = [
    { value: '', label: 'Barcha xonalar' },
    { value: "2 o'rinli standart", label: "2 o'rinli standart" },
    { value: "4 o'rinli standart", label: "4 o'rinli standart" },
    { value: "2 o'rinli lyuks", label: "2 o'rinli lyuks" },
    { value: "4 o'rinli kichik VIP", label: "4 o'rinli kichik VIP" },
    { value: "4 o'rinli katta VIP", label: "4 o'rinli katta VIP" },
    { value: "4 o'rinli apartament", label: "4 o'rinli apartament" },
    { value: "Kottedj (6 kishi uchun)", label: "Kottedj" },
    { value: "Prezident apartamenti (8 kishi uchun)", label: "Prezident apartamenti" }
  ];

  const handleTypeChange = (e) => {
    onChange({ ...filters, type: e.target.value });
  };

  const handleStatusChange = (e) => {
    onChange({ ...filters, status: e.target.value });
  };

  return (
    <Card>
      <CardContent className="p-4 space-y-4">
        <h3 className="font-medium text-gray-900">{t('filter')}</h3>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            {t('roomType')}
          </label>
          <select
            value={filters.type || ''}
            onChange={handleTypeChange}
            className="w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
          >
            {roomTypes.map(type => (
              <option key={type.value} value={type.value}>
                {type.label}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            {t('status')}
          </label>
          <select
            value={filters.status || ''}
            onChange={handleStatusChange}
            className="w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
          >
            <option value="">Barcha</option>
            <option value="available">{t('available')}</option>
            <option value="occupied">{t('occupied')}</option>
          </select>
        </div>
      </CardContent>
    </Card>
  );
}