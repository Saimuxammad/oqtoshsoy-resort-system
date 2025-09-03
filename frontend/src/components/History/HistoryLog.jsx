import React, { useState, useEffect } from 'react';
import { Card, CardContent } from '../UI/Card';
import { Loading } from '../UI/Loading';
import { ClockIcon, UserIcon, DocumentTextIcon, TrashIcon, PlusIcon, PencilIcon } from '@heroicons/react/24/outline';
import { format } from 'date-fns';
import { uz } from 'date-fns/locale';

export function HistoryLog() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = () => {
    try {
      setLoading(true);

      // Симулируем историю действий из localStorage
      const savedHistory = localStorage.getItem('action_history');
      let historyData = savedHistory ? JSON.parse(savedHistory) : [];

      // Если истории нет, создаем примеры
      if (historyData.length === 0) {
        historyData = [
          {
            id: 1,
            action: 'create',
            entity: 'booking',
            description: 'Xona №21 bronlandi',
            user: 'Admin',
            timestamp: new Date().toISOString(),
            details: { room: '21', dates: '06.09.2025 - 10.09.2025' }
          },
          {
            id: 2,
            action: 'update',
            entity: 'booking',
            description: 'Bron yangilandi',
            user: 'Admin',
            timestamp: new Date(Date.now() - 3600000).toISOString(),
            details: { room: '22', change: 'Mehmon ismi o\'zgartirildi' }
          },
          {
            id: 3,
            action: 'delete',
            entity: 'booking',
            description: 'Bron bekor qilindi',
            user: 'Admin',
            timestamp: new Date(Date.now() - 7200000).toISOString(),
            details: { room: '20' }
          },
          {
            id: 4,
            action: 'login',
            entity: 'system',
            description: 'Tizimga kirish',
            user: 'Admin',
            timestamp: new Date(Date.now() - 86400000).toISOString(),
            details: {}
          }
        ];
        localStorage.setItem('action_history', JSON.stringify(historyData));
      }

      setHistory(historyData.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp)));
    } catch (error) {
      console.error('History load error:', error);
      setHistory([]);
    } finally {
      setLoading(false);
    }
  };

  const getActionIcon = (action) => {
    switch (action) {
      case 'create':
        return <PlusIcon className="h-5 w-5 text-green-500" />;
      case 'update':
        return <PencilIcon className="h-5 w-5 text-blue-500" />;
      case 'delete':
        return <TrashIcon className="h-5 w-5 text-red-500" />;
      default:
        return <DocumentTextIcon className="h-5 w-5 text-gray-500" />;
    }
  };

  const getActionColor = (action) => {
    switch (action) {
      case 'create':
        return 'bg-green-100 text-green-800';
      case 'update':
        return 'bg-blue-100 text-blue-800';
      case 'delete':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const filteredHistory = filter === 'all'
    ? history
    : history.filter(item => item.entity === filter);

  if (loading) return <Loading />;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">Harakatlar tarixi</h2>

        <div className="flex gap-2">
          <button
            onClick={() => setFilter('all')}
            className={`px-4 py-2 rounded-lg ${
              filter === 'all' ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-700'
            }`}
          >
            Barchasi
          </button>
          <button
            onClick={() => setFilter('booking')}
            className={`px-4 py-2 rounded-lg ${
              filter === 'booking' ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-700'
            }`}
          >
            Bronlar
          </button>
          <button
            onClick={() => setFilter('system')}
            className={`px-4 py-2 rounded-lg ${
              filter === 'system' ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-700'
            }`}
          >
            Tizim
          </button>
        </div>
      </div>

      {filteredHistory.length === 0 ? (
        <Card>
          <CardContent className="text-center py-12 text-gray-500">
            <ClockIcon className="h-12 w-12 mx-auto mb-4 text-gray-400" />
            <p>Harakatlar tarixi bo'sh</p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {/* Timeline */}
          <div className="relative">
            <div className="absolute left-8 top-0 bottom-0 w-0.5 bg-gray-200"></div>

            {filteredHistory.map((item, index) => (
              <div key={item.id} className="relative flex items-start mb-6">
                {/* Icon */}
                <div className="absolute left-6 bg-white p-1 rounded-full border-2 border-gray-200">
                  {getActionIcon(item.action)}
                </div>

                {/* Content */}
                <Card className="ml-16 flex-1">
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getActionColor(item.action)}`}>
                            {item.action.toUpperCase()}
                          </span>
                          <span className="text-sm text-gray-600">
                            {format(new Date(item.timestamp), 'dd MMMM yyyy, HH:mm', { locale: uz })}
                          </span>
                        </div>

                        <p className="text-gray-900 font-medium">{item.description}</p>

                        {item.details && Object.keys(item.details).length > 0 && (
                          <div className="mt-2 text-sm text-gray-600">
                            {item.details.room && <p>Xona: №{item.details.room}</p>}
                            {item.details.dates && <p>Sanalar: {item.details.dates}</p>}
                            {item.details.change && <p>O'zgarish: {item.details.change}</p>}
                          </div>
                        )}

                        <div className="mt-2 flex items-center gap-2 text-xs text-gray-500">
                          <UserIcon className="h-3 w-3" />
                          <span>{item.user}</span>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}