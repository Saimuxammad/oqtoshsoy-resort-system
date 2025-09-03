import React, { useState, useEffect } from 'react';
import { RoomCard } from './RoomCard';
import { RoomFilter } from './RoomFilter';
import { Loading } from '../UI/Loading';
import { Button } from '../UI/Button';
import { ArrowPathIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';
import { roomService } from '../../services/roomService';

export function RoomList({ onEditRoom, onViewCalendar }) {
  const [filters, setFilters] = useState({});
  const [rooms, setRooms] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadRooms = async () => {
    try {
      setIsLoading(true);
      setError(null);

      console.log('[RoomList] Loading rooms with filters:', filters);

      // Используем roomService для получения комнат
      const data = await roomService.getRooms(filters);

      console.log('[RoomList] Received rooms:', data.length);

      if (Array.isArray(data)) {
        setRooms(data);
        toast.success(`${data.length} xona yuklandi`);
      } else {
        console.error('[RoomList] Data is not an array:', data);
        setRooms([]);
        toast.error('Xonalar formatida xatolik');
      }
    } catch (err) {
      console.error('[RoomList] Load rooms error:', err);
      setError(err.message || 'Xonalarni yuklashda xatolik');
      toast.error('Xonalarni yuklashda xatolik');
      setRooms([]);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadRooms();
  }, [filters]); // Перезагружаем при изменении фильтров

  const handleRefresh = () => {
    loadRooms();
  };

  const handleFilterChange = (newFilters) => {
    console.log('[RoomList] Filter changed:', newFilters);
    setFilters(newFilters);
  };

  if (isLoading) return <Loading />;

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600 mb-4">Xatolik yuz berdi</p>
        <p className="text-gray-600 mb-4">{error}</p>
        <Button onClick={handleRefresh} variant="secondary">
          <ArrowPathIcon className="h-4 w-4 mr-2" />
          Qayta urinish
        </Button>
      </div>
    );
  }

  // Группируем комнаты по типу для удобного отображения
  const groupedRooms = rooms.reduce((groups, room) => {
    const type = room.room_type;
    if (!groups[type]) {
      groups[type] = [];
    }
    groups[type].push(room);
    return groups;
  }, {});

  return (
    <div className="flex flex-col lg:flex-row gap-6">
      <div className="lg:w-64 flex-shrink-0">
        <RoomFilter filters={filters} onChange={handleFilterChange} />
      </div>

      <div className="flex-1">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-gray-900">
            Xonalar ro'yxati ({rooms.length})
          </h2>
          <Button
            variant="secondary"
            size="sm"
            onClick={handleRefresh}
          >
            <ArrowPathIcon className="h-4 w-4 mr-2" />
            Qayta yuklash
          </Button>
        </div>

        {rooms.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-gray-500">
              <p className="text-lg mb-2">Xonalar topilmadi</p>
              {filters.type && (
                <p className="text-sm">Filterni o'chirib ko'ring</p>
              )}
            </div>
          </div>
        ) : (
          <div>
            {/* Отображаем комнаты сгруппированными или все вместе */}
            {filters.type ? (
              // Если выбран фильтр - показываем простой список
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {rooms.map((room) => (
                  <RoomCard
                    key={room.id}
                    room={room}
                    onEdit={onEditRoom}
                    onViewCalendar={onViewCalendar}
                  />
                ))}
              </div>
            ) : (
              // Если фильтр не выбран - группируем по типам
              <div className="space-y-6">
                {Object.entries(groupedRooms).map(([type, typeRooms]) => (
                  <div key={type}>
                    <h3 className="text-lg font-semibold text-gray-800 mb-3">
                      {type} ({typeRooms.length} ta)
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                      {typeRooms.map((room) => (
                        <RoomCard
                          key={room.id}
                          room={room}
                          onEdit={onEditRoom}
                          onViewCalendar={onViewCalendar}
                        />
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}