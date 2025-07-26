import React, { useState } from 'react';
import { Button } from '../UI/Button';
import { DatePicker } from './DatePicker';

export function BookingForm({ room, booking, onSubmit, onCancel }) {
  const [formData, setFormData] = useState({
    start_date: booking?.start_date ? new Date(booking.start_date) : new Date(),
    end_date: booking?.end_date ? new Date(booking.end_date) : new Date(),
    guest_name: booking?.guest_name || '',
    notes: booking?.notes || ''
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit({
      ...formData,
      room_id: room.id,
      start_date: formData.start_date.toISOString().split('T')[0],
      end_date: formData.end_date.toISOString().split('T')[0]
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="bg-gray-50 p-3 rounded-lg">
        <p className="text-sm text-gray-600">
          Xona: <span className="font-medium">№{room.room_number}</span>
        </p>
        <p className="text-sm text-gray-600">
          Turi: <span className="font-medium">{room.room_type}</span>
        </p>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <DatePicker
          label="Kirish sanasi"
          selected={formData.start_date}
          onChange={(date) => setFormData({ ...formData, start_date: date })}
          minDate={new Date()}
        />

        <DatePicker
          label="Chiqish sanasi"
          selected={formData.end_date}
          onChange={(date) => setFormData({ ...formData, end_date: date })}
          minDate={formData.start_date}
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Mehmon ismi
        </label>
        <input
          type="text"
          value={formData.guest_name}
          onChange={(e) => setFormData({ ...formData, guest_name: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
          placeholder="Mehmon ismi (ixtiyoriy)"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Izohlar
        </label>
        <textarea
          value={formData.notes}
          onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
          rows={3}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
          placeholder="Qo'shimcha ma'lumotlar (ixtiyoriy)"
        />
      </div>

      <div className="flex gap-3 pt-4">
        <Button type="submit" className="flex-1">
          {booking ? 'Yangilash' : 'Saqlash'}
        </Button>
        <Button type="button" variant="secondary" onClick={onCancel}>
          Bekor qilish
        </Button>
      </div>
    </form>
  );
}
