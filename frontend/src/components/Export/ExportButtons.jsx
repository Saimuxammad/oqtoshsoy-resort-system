import React from 'react';
import { Button } from '../UI/Button';
import { ArrowDownTrayIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

export function ExportButtons() {
  const handleExportBookings = () => {
    const url = 'https://oqtoshsoy-resort-system-production-ef7c.up.railway.app/api/export/bookings';
    window.open(url, '_blank');
    toast.success("Bronlar yuklanmoqda...");
  };

  const handleExportRooms = () => {
    const url = 'https://oqtoshsoy-resort-system-production-ef7c.up.railway.app/api/export/rooms';
    window.open(url, '_blank');
    toast.success("Xonalar ro'yxati yuklanmoqda...");
  };

  return (
    <div className="flex gap-3">
      <Button
        variant="secondary"
        onClick={handleExportBookings}
        className="flex items-center gap-2"
      >
        <ArrowDownTrayIcon className="h-4 w-4" />
        Bronlarni yuklash
      </Button>

      <Button
        variant="secondary"
        onClick={handleExportRooms}
        className="flex items-center gap-2"
      >
        <ArrowDownTrayIcon className="h-4 w-4" />
        Xonalarni yuklash
      </Button>
    </div>
  );
}