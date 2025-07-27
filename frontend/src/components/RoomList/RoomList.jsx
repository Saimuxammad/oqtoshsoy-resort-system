import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { roomService } from '../../services/roomService';
import { RoomCard } from './RoomCard';
import { RoomFilter } from './RoomFilter';
import { Loading } from '../UI/Loading';
import { Button } from '../UI/Button';
import { ArrowPathIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

// ВАЖНО: Используем именованный экспорт
export function RoomList({ onEditRoom, onViewCalendar }) {
  const [filters, setFilters] = useState({});

  const { data: rooms, isLoading, error, refetch } = useQuery(
    ['rooms', filters],
    () => roomService.getRooms(filters),
    {
      onError: (error) => {
        console.error('Room fetch error:', error);
        toast.error(`Xonalarni yuklashda xatolik: ${error.message}`);
      },
      onSuccess: (data) => {
        console.log('Rooms loaded successfully:', data);
      }
    }
  );

  const handleRefresh = () => {
    refetch();
    toast.success('Yangilandi');
  };

  // Group rooms by type
  const groupedRooms = rooms?.reduce((acc, room) => {
    const type = room.room_type;
    if (!acc[type]) acc[type] = [];
    acc[type].push(room);
    return acc;
  }, {}) || {};

  if (isLoading) return <Loading />;

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600 mb-4">Xatolik yuz berdi</p>
        <p className="text-gray-600 mb-4">{error.message}</p>
        <Button onClick={handleRefresh} variant="secondary">
          <ArrowPathIcon className="h-4 w-4 mr-2" />
          Qayta urinish
        </Button>
      </div>
    );
  }

  return (
    <div className="flex flex-col lg:flex-row gap-6">
      {/* Filters - Sidebar on desktop, top on mobile */}
      <div className="lg:w-64 flex-shrink-0">
        <RoomFilter filters={filters} onChange={setFilters} />
      </div>

      {/* Room List */}
      <div className="flex-1">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-gray-900">
            Xonalar ro'yxati {rooms && `(${rooms.length})`}
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

        {!rooms || rooms.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            <p>Xonalar topilmadi</p>
            <p className="text-sm mt-2">Backend serverini tekshiring</p>
          </div>
        ) : Object.keys(groupedRooms).length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            <p>Filtrlangan xonalar topilmadi</p>
          </div>
        ) : (
          <div className="space-y-6">
            {Object.entries(groupedRooms).map(([type, typeRooms]) => (
              <div key={type}>
                <h3 className="text-lg font-medium text-gray-800 mb-3">
                  {type} ({typeRooms.length})
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
    </div>
  );
}