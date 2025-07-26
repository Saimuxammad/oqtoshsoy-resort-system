import React from 'react';
import { Card, CardHeader, CardContent } from '../UI/Card';
import { Button } from '../UI/Button';
import { useLanguage } from '../../contexts/LanguageContext';
import { useTelegram } from '../../hooks/useTelegram';
import {
  LanguageIcon,
  BellIcon,
  MoonIcon,
  SunIcon
} from '@heroicons/react/24/outline';

export function SettingsPanel() {
  const { t, language, changeLanguage } = useLanguage();
  const { user } = useTelegram();
  const [notifications, setNotifications] = React.useState(true);
  const [theme, setTheme] = React.useState('light');

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-semibold text-gray-900">{t('settings')}</h2>

      {/* Language Settings */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <LanguageIcon className="h-5 w-5 text-gray-600" />
            <h3 className="text-lg font-medium">{t('language')}</h3>
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex gap-3">
            <Button
              variant={language === 'uz' ? 'primary' : 'secondary'}
              onClick={() => changeLanguage('uz')}
            >
              O'zbek
            </Button>
            <Button
              variant={language === 'ru' ? 'primary' : 'secondary'}
              onClick={() => changeLanguage('ru')}
            >
              Русский
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Notification Settings */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <BellIcon className="h-5 w-5 text-gray-600" />
            <h3 className="text-lg font-medium">{t('notifications')}</h3>
          </div>
        </CardHeader>
        <CardContent>
          <label className="flex items-center gap-3 cursor-pointer">
            <input
              type="checkbox"
              checked={notifications}
              onChange={(e) => setNotifications(e.target.checked)}
              className="w-4 h-4 text-primary-600 rounded focus:ring-primary-500"
            />
            <span className="text-sm text-gray-700">{t('enableNotifications')}</span>
          </label>
        </CardContent>
      </Card>

      {/* Theme Settings */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            {theme === 'light' ? (
              <SunIcon className="h-5 w-5 text-gray-600" />
            ) : (
              <MoonIcon className="h-5 w-5 text-gray-600" />
            )}
            <h3 className="text-lg font-medium">{t('theme')}</h3>
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex gap-3">
            <Button
              variant={theme === 'light' ? 'primary' : 'secondary'}
              onClick={() => setTheme('light')}
            >
              <SunIcon className="h-4 w-4 mr-2" />
              {t('lightTheme')}
            </Button>
            <Button
              variant={theme === 'dark' ? 'primary' : 'secondary'}
              onClick={() => setTheme('dark')}
            >
              <MoonIcon className="h-4 w-4 mr-2" />
              {t('darkTheme')}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* User Info */}
      <Card>
        <CardHeader>
          <h3 className="text-lg font-medium">{t('user')}</h3>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <p className="text-sm text-gray-600">
              <span className="font-medium">ID:</span> {user?.id}
            </p>
            <p className="text-sm text-gray-600">
              <span className="font-medium">Name:</span> {user?.first_name} {user?.last_name || ''}
            </p>
            {user?.username && (
              <p className="text-sm text-gray-600">
                <span className="font-medium">Username:</span> @{user.username}
              </p>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}