import React, { useState } from 'react';
import { format, startOfMonth, endOfMonth, eachDayOfInterval, isSameMonth, isToday, getDay, startOfWeek, endOfWeek } from 'date-fns';
import { uz } from 'date-fns/locale';
import { ChevronLeftIcon, ChevronRightIcon } from '@heroicons/react/24/outline';
import { useQuery } from 'react-query';
import { bookingService } from '../../services/bookingService';
import { Button } from '../UI/Button';
import clsx from 'clsx';

export function CalendarView({ selectedRoom }) {
  const [currentDate, setCurrentDate] = useState(new Date());

  const monthStart = startOfMonth(currentDate);
  const monthEnd = endOfMonth(currentDate);
  const calendarStart = startOfWeek(monthStart, { weekStartsOn: 1 }); // Start from Monday
  const calendarEnd = endOfWeek(monthEnd, { weekStartsOn: 1 });

  const { data: bookings = [] } = useQuery(
    ['bookings', selectedRoom?.id, monthStart, monthEnd],
    () => bookingService.getBookings({
      roomId: selectedRoom?.id,
      startDate: format(monthStart, 'yyyy-MM-dd'),
      endDate: format(monthEnd, 'yyyy-MM-dd')
    }),
    {
      enabled: !!selectedRoom
    }
  );

  const days = eachDayOfInterval({ start: calendarStart, end: calendarEnd });

  const isBooked = (date) => {
    return bookings.some(booking => {
      const start = new Date(booking.start_date);
      const end = new Date(booking.end_date);
      return date >= start && date <= end;
    });
  };

  const prevMonth = () => {
    setCurrentDate(prev => new Date(prev.getFullYear(), prev.getMonth() - 1));
  };

  const nextMonth = () => {
    setCurrentDate(prev => new Date(prev.getFullYear(), prev.getMonth() + 1));
  };

  if (!selectedRoom) {
    return (
      <div className="text-center py-12 text-gray-500">
        Kalendar ko'rish uchun xona tanlang
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-lg font-semibold text-gray-900">
          №{selectedRoom.room_number} - {selectedRoom.room_type}
        </h2>

        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={prevMonth}
          >
            <ChevronLeftIcon className="h-4 w-4" />
          </Button>

          <span className="px-3 font-medium text-gray-900">
            {format(currentDate, 'MMMM yyyy', { locale: uz })}
          </span>

          <Button
            variant="ghost"
            size="sm"
            onClick={nextMonth}
          >
            <ChevronRightIcon className="h-4 w-4" />
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-7 gap-1">
        {['Du', 'Se', 'Ch', 'Pa', 'Ju', 'Sh', 'Ya'].map(day => (
          <div key={day} className="text-center text-xs font-medium text-gray-700 py-2">
            {day}
          </div>
        ))}

        {days.map((day, idx) => {
          const booked = isBooked(day);
          const today = isToday(day);
          const isCurrentMonth = isSameMonth(day, currentDate);

          return (
            <div
              key={idx}
              className={clsx(
                'aspect-square flex items-center justify-center text-sm rounded-lg relative',
                {
                  'bg-red-100': booked,
                  'bg-primary-100': today && !booked,
                  'hover:bg-gray-100': !booked && !today && isCurrentMonth,
                  'text-gray-400': !isCurrentMonth,
                  'text-gray-900': isCurrentMonth && !booked,
                  'text-red-800 font-medium': booked,
                  'text-primary-800 font-semibold': today && !booked,
                }
              )}
            >
              <span>{format(day, 'd')}</span>
            </div>
          );
        })}
      </div>

      <div className="mt-6 space-y-2">
        <div className="flex items-center gap-2 text-sm">
          <div className="w-4 h-4 bg-red-100 rounded"></div>
          <span className="text-gray-600">Band kunlar</span>
        </div>
        <div className="flex items-center gap-2 text-sm">
          <div className="w-4 h-4 bg-primary-100 rounded"></div>
          <span className="text-gray-600">Bugun</span>
        </div>
      </div>
    </div>
  );
}