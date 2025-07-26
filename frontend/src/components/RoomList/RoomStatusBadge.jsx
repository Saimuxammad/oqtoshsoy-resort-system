import React from 'react';
import clsx from 'clsx';
import { format } from 'date-fns';
import { uz } from 'date-fns/locale';

export function RoomStatusBadge({ isAvailable, booking }) {
  if (isAvailable) {
    return (
      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
        <span className="w-2 h-2 mr-1 bg-green-400 rounded-full"></span>
        Bo'sh
      </span>
    );
  }

  const formatDate = (date) => {
    return format(new Date(date), 'd-MMM', { locale: uz });
  };

  return (
    <div className="flex flex-col items-start">
      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
        <span className="w-2 h-2 mr-1 bg-red-400 rounded-full"></span>
        Band
      </span>
      {booking && (
        <span className="mt-1 text-xs text-gray-600">
          {formatDate(booking.start_date)} → {formatDate(booking.end_date)}
        </span>
      )}
    </div>
  );
}