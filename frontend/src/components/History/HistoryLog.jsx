import React from 'react';
import { useQuery } from 'react-query';
import { Card, CardHeader, CardContent } from '../UI/Card';
import { Loading } from '../UI/Loading';
import { useLanguage } from '../../contexts/LanguageContext';
import { historyService } from '../../services/historyService';
import { format } from 'date-fns';
import { uz, ru } from 'date-fns/locale';
import {
  ClockIcon,
  UserIcon,
  PencilIcon,
  PlusIcon,
  TrashIcon
} from '@heroicons/react/24/outline';

export function HistoryLog() {
  const { t, language } = useLanguage();
  const locale = language === 'uz' ? uz : ru;

  const { data: history, isLoading } = useQuery(
    ['history', 'recent'],
    () => historyService.getRecentHistory(24)
  );

  if (isLoading) return <Loading />;

  const getActionIcon = (action) => {
    switch (action) {
      case 'create':
        return <PlusIcon className="h-4 w-4 text-green-600" />;
      case 'update':
        return <PencilIcon className="h-4 w-4 text-blue-600" />;
      case 'delete':
        return <TrashIcon className="h-4 w-4 text-red-600" />;
      default:
        return <ClockIcon className="h-4 w-4 text-gray-600" />;
    }
  };

  const getActionText = (action) => {
    switch (action) {
      case 'create':
        return t('created');
      case 'update':
        return t('updated');
      case 'delete':
        return t('deleted');
      default:
        return action;
    }
  };

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold text-gray-900">{t('actionHistory')}</h2>

      <Card>
        <CardHeader>
          <h3 className="text-lg font-medium">{t('recentActivity')}</h3>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {history && history.length > 0 ? (
              history.map((log) => (
                <div key={log.id} className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
                  <div className="flex-shrink-0 mt-1">
                    {getActionIcon(log.action)}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2 text-sm">
                      <UserIcon className="h-4 w-4 text-gray-400" />
                      <span className="font-medium">{log.user?.first_name} {log.user?.last_name}</span>
                      <span className="text-gray-500">{getActionText(log.action)}</span>
                      <span className="text-gray-700">{log.entity_type}</span>
                    </div>
                    {log.description && (
                      <p className="mt-1 text-sm text-gray-600">{log.description}</p>
                    )}
                    <p className="mt-1 text-xs text-gray-500">
                      {format(new Date(log.created_at), 'dd MMMM yyyy, HH:mm', { locale })}
                    </p>
                  </div>
                </div>
              ))
            ) : (
              <p className="text-center text-gray-500 py-8">{t('noData')}</p>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}