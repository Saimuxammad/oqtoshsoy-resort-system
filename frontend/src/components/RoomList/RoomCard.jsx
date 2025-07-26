import React from 'react';
import { Card, CardContent } from '../UI/Card';
import { Button } from '../UI/Button';
import { RoomStatusBadge } from './RoomStatusBadge';
import { CalendarDaysIcon, PencilIcon } from '@heroicons/react/24/outline';

export function RoomCard({ room, onEdit, onViewCalendar }) {
  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardContent className="p-4">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <h3 className="text-lg font-semibold text-gray-900">
                №{room.room_number}
              </h3>
              <RoomStatusBadge
                isAvailable={room.is_available}
                booking={room.current_booking}
              />
            </div>

            <p className="text-sm text-gray-600 mb-3">
              {room.room_type}
            </p>

            {room.current_booking?.guest_name && (
              <p className="text-xs text-gray-500">
                Mehmon: {room.current_booking.guest_name}
              </p>
            )}
          </div>

          <div className="flex gap-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onViewCalendar(room)}
              title="Kalendar"
            >
              <CalendarDaysIcon className="h-4 w-4" />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onEdit(room)}
              title="Tahrirlash"
            >
              <PencilIcon className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}