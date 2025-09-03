import React, { useState, useEffect } from 'react';
import { Card, CardContent } from '../UI/Card';
import { Button } from '../UI/Button';
import {
  UserIcon,
  BellIcon,
  LanguageIcon,
  PaintBrushIcon,
  ShieldCheckIcon,
  CurrencyDollarIcon,
  DocumentTextIcon,
  CogIcon
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

export function SettingsPanel() {
  const [settings, setSettings] = useState({
    language: 'uz',
    notifications: true,
    emailNotifications: false,
    telegramNotifications: true,
    darkMode: false,
    currency: 'UZS',
    dateFormat: 'DD.MM.YYYY',
    autoBackup: true,
    priceDisplay: 'full'
  });

  const [userInfo, setUserInfo] = useState({
    name: 'Admin',
    role: 'Administrator',
    email: 'admin@oqtoshsoy.uz',
    phone: '+998 90 123 45 67',
    telegram: '@admin_oqtoshsoy'
  });

  useEffect(() => {
    // Load settings from localStorage
    const saved = localStorage.getItem('app_settings');
    if (saved) {
      setSettings(JSON.parse(saved));
    }
  }, []);

  const handleSettingChange = (key, value) => {
    const newSettings = { ...settings, [key]: value };
    setSettings(newSettings);
    localStorage.setItem('app_settings', JSON.stringify(newSettings));
    toast.success('Sozlama saqlandi');
  };

  const handleUserInfoSave = () => {
    localStorage.setItem('user_info', JSON.stringify(userInfo));
    toast.success('Foydalanuvchi ma\'lumotlari yangilandi');
  };

  const handleExportData = () => {
    // Export all data as JSON
    const data = {
      settings,
      userInfo,
      exportDate: new Date().toISOString()
    };

    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `oqtoshsoy_backup_${new Date().toISOString().split('T')[0]}.json`;
    a.click();

    toast.success('Ma\'lumotlar eksport qilindi');
  };

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-900">Sozlamalar</h2>

      {/* User Profile */}
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center mb-4">
            <UserIcon className="h-6 w-6 mr-2 text-gray-600" />
            <h3 className="text-lg font-semibold">Foydalanuvchi profili</h3>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Ism</label>
              <input
                type="text"
                value={userInfo.name}
                onChange={(e) => setUserInfo({ ...userInfo, name: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Rol</label>
              <select
                value={userInfo.role}
                onChange={(e) => setUserInfo({ ...userInfo, role: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="Administrator">Administrator</option>
                <option value="Manager">Menejer</option>
                <option value="Operator">Operator</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
              <input
                type="email"
                value={userInfo.email}
                onChange={(e) => setUserInfo({ ...userInfo, email: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Telefon</label>
              <input
                type="tel"
                value={userInfo.phone}
                onChange={(e) => setUserInfo({ ...userInfo, phone: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Telegram</label>
              <input
                type="text"
                value={userInfo.telegram}
                onChange={(e) => setUserInfo({ ...userInfo, telegram: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          <Button onClick={handleUserInfoSave} className="mt-4">
            Saqlash
          </Button>
        </CardContent>
      </Card>

      {/* Notifications */}
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center mb-4">
            <BellIcon className="h-6 w-6 mr-2 text-gray-600" />
            <h3 className="text-lg font-semibold">Bildirishnomalar</h3>
          </div>

          <div className="space-y-3">
            <label className="flex items-center justify-between">
              <span className="text-sm text-gray-700">Bildirishnomalarni yoqish</span>
              <input
                type="checkbox"
                checked={settings.notifications}
                onChange={(e) => handleSettingChange('notifications', e.target.checked)}
                className="toggle"
              />
            </label>

            <label className="flex items-center justify-between">
              <span className="text-sm text-gray-700">Email bildirishnomalar</span>
              <input
                type="checkbox"
                checked={settings.emailNotifications}
                onChange={(e) => handleSettingChange('emailNotifications', e.target.checked)}
                className="toggle"
              />
            </label>

            <label className="flex items-center justify-between">
              <span className="text-sm text-gray-700">Telegram bildirishnomalar</span>
              <input
                type="checkbox"
                checked={settings.telegramNotifications}
                onChange={(e) => handleSettingChange('telegramNotifications', e.target.checked)}
                className="toggle"
              />
            </label>
          </div>
        </CardContent>
      </Card>

      {/* System Settings */}
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center mb-4">
            <CogIcon className="h-6 w-6 mr-2 text-gray-600" />
            <h3 className="text-lg font-semibold">Tizim sozlamalari</h3>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                <LanguageIcon className="h-4 w-4 inline mr-1" />
                Til
              </label>
              <select
                value={settings.language}
                onChange={(e) => handleSettingChange('language', e.target.value)}
                className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="uz">O'zbekcha</option>
                <option value="ru">Русский</option>
                <option value="en">English</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                <CurrencyDollarIcon className="h-4 w-4 inline mr-1" />
                Valyuta
              </label>
              <select
                value={settings.currency}
                onChange={(e) => handleSettingChange('currency', e.target.value)}
                className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="UZS">UZS (so'm)</option>
                <option value="USD">USD ($)</option>
                <option value="EUR">EUR (€)</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Sana formati
              </label>
              <select
                value={settings.dateFormat}
                onChange={(e) => handleSettingChange('dateFormat', e.target.value)}
                className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="DD.MM.YYYY">DD.MM.YYYY</option>
                <option value="MM/DD/YYYY">MM/DD/YYYY</option>
                <option value="YYYY-MM-DD">YYYY-MM-DD</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Narx ko'rinishi
              </label>
              <select
                value={settings.priceDisplay}
                onChange={(e) => handleSettingChange('priceDisplay', e.target.value)}
                className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="full">To'liq (1,000,000)</option>
                <option value="short">Qisqa (1M)</option>
              </select>
            </div>
          </div>

          <div className="mt-4 space-y-3">
            <label className="flex items-center justify-between">
              <span className="text-sm text-gray-700">Avtomatik zahira nusxa</span>
              <input
                type="checkbox"
                checked={settings.autoBackup}
                onChange={(e) => handleSettingChange('autoBackup', e.target.checked)}
                className="toggle"
              />
            </label>

            <label className="flex items-center justify-between">
              <span className="text-sm text-gray-700">Qorong'u rejim</span>
              <input
                type="checkbox"
                checked={settings.darkMode}
                onChange={(e) => handleSettingChange('darkMode', e.target.checked)}
                className="toggle"
              />
            </label>
          </div>
        </CardContent>
      </Card>

      {/* Data Management */}
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center mb-4">
            <DocumentTextIcon className="h-6 w-6 mr-2 text-gray-600" />
            <h3 className="text-lg font-semibold">Ma'lumotlarni boshqarish</h3>
          </div>

          <div className="flex flex-wrap gap-3">
            <Button onClick={handleExportData} variant="secondary">
              Ma'lumotlarni eksport qilish
            </Button>

            <Button variant="secondary" onClick={() => toast.info('Import funksiyasi tez orada')}>
              Ma'lumotlarni import qilish
            </Button>

            <Button
              variant="danger"
              onClick={() => {
                if (window.confirm('Barcha ma\'lumotlar o\'chiriladi. Davom etasizmi?')) {
                  localStorage.clear();
                  toast.success('Barcha ma\'lumotlar tozalandi');
                  window.location.reload();
                }
              }}
            >
              Keshni tozalash
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* System Info */}
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center mb-4">
            <ShieldCheckIcon className="h-6 w-6 mr-2 text-gray-600" />
            <h3 className="text-lg font-semibold">Tizim haqida</h3>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-gray-600">Versiya:</span>
              <span className="ml-2 font-medium">2.0.0</span>
            </div>
            <div>
              <span className="text-gray-600">Oxirgi yangilanish:</span>
              <span className="ml-2 font-medium">03.09.2025</span>
            </div>
            <div>
              <span className="text-gray-600">Server holati:</span>
              <span className="ml-2 font-medium text-green-600">Faol</span>
            </div>
            <div>
              <span className="text-gray-600">API versiyasi:</span>
              <span className="ml-2 font-medium">v2</span>
            </div>
          </div>
        </CardContent>
      </Card>
        </>
      );
}