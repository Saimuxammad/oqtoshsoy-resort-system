import React, { useState, useEffect } from 'react';
import { RoomCard } from './RoomCard';
import { RoomFilter } from './RoomFilter';
import { Loading } from '../UI/Loading';
import { Button } from '../UI/Button';
import { ArrowPathIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

export function RoomList({ onEditRoom, onViewCalendar }) {
  const [filters, setFilters] = useState({});
  const [rooms, setRooms] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadRooms = async () => {
    try {
      setIsLoading(true);
      setError(null);

      // Прямой fetch без использования сервисов
      const response = await fetch('https://oqtoshsoy-resort-system-production.up.railway.app/api/rooms');
      const data = await response.json();

      console.log('Direct fetch - rooms count:', data.length);
      console.log('First 3 rooms:', data.slice(0, 3));

      // Преобразуем типы комнат
      const roomTypeMap = {
        'STANDARD_2': "2 o'rinli standart",
        'STANDARD_4': "4 o'rinli standart",
        'LUX_2': "2 o'rinli lyuks",
        'VIP_SMALL_4': "4 o'rinli kichik VIP",
        'VIP_BIG_4': "4 o'rinli katta VIP",
        'APARTMENT_4': "4 o'rinli apartament",
        'COTTAGE_6': "Kottedj (6 kishi uchun)",
        'PRESIDENT_8': "Prezident apartamenti (8 kishi uchun)"
      };

      const transformedRooms = data.map(room => ({
        ...room,
        room_type: roomTypeMap[room.room_type] || room.room_type
      }));

      setRooms(transformedRooms);
      toast.success(`${transformedRooms.length} xona yuklandi`);
    } catch (err) {
      console.error('Load rooms error:', err);
      setError(err.message);
      toast.error('Xonalarni yuklashda xatolik');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadRooms();
  }, []);

  const handleRefresh = () => {
    loadRooms();
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

  return (
    <div className="flex flex-col lg:flex-row gap-6">
      <div className="lg:w-64 flex-shrink-0">
        <RoomFilter filters={filters} onChange={setFilters} />
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
          <div className="text-center py-12 text-gray-500">
            <p>Xonalar topilmadi</p>
          </div>
        ) : (
          <div>
            <div className="mb-4 p-4 bg-blue-50 rounded-lg">
              <p className="text-sm text-blue-800">
                Jami {rooms.length} xona topildi
              </p>
            </div>

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
          </div>
        )}
      </div>
    </div>
  );
}