import React from 'react';
import { ExclamationTriangleIcon } from '@heroicons/react/24/outline';

export function AccessDenied({ message }) {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8 text-center">
        <div className="flex justify-center mb-4">
          <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center">
            <ExclamationTriangleIcon className="w-8 h-8 text-red-600" />
          </div>
        </div>

        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Kirish rad etildi
        </h2>

        <p className="text-gray-600 mb-6">
          {message || 'Sizga ushbu tizimdan foydalanish uchun ruxsat berilmagan.'}
        </p>

        <div className="space-y-2 text-sm text-gray-500">
          <p>Agar bu xato deb hisoblasangiz:</p>
          <p>Tizim administratoriga murojaat qiling</p>
          <p className="font-mono text-xs">@Oqtosh_Soy</p>
        </div>
      </div>
    </div>
  );
}