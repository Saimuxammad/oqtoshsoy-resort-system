import React from 'react';
import { useTelegram } from '../../hooks/useTelegram';

export function Header() {
  const { user } = useTelegram();

  return (
    <header className="bg-primary-700 text-white shadow-lg">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center gap-4">
            <img
              src="/logo.png"
              alt="Oqtoshsoy Resort"
              className="h-10 w-auto"
            />
            <div>
              <h1 className="text-xl font-semibold">Oqtoshsoy Resort</h1>
              <p className="text-xs text-primary-200">Xonalarni boshqarish tizimi</p>
            </div>
          </div>

          {user && (
            <div className="text-right">
              <p className="text-sm font-medium">
                {user.first_name} {user.last_name || ''}
              </p>
              <p className="text-xs text-primary-200">
                @{user.username || user.id}
              </p>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}