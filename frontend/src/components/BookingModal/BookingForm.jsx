import React, { useState, useEffect } from 'react';
import { Button } from '../UI/Button';
import { DatePicker } from './DatePicker';
import { TrashIcon, ArrowRightIcon } from '@heroicons/react/24/outline';

export function BookingForm({ room, booking, onSubmit, onCancel, onDelete, onExtend, isLoading }) {
  const [formData, setFormData] = useState({
    start_date: booking?.start_date ? new Date(booking.start_date) : new Date(),
    end_date: booking?.end_date ? new Date(booking.end_date) : new Date(),
    guest_name: booking?.guest_name || '',
    notes: booking?.notes || ''
  });

  const [isExtending, setIsExtending] = useState(false);

  // Если режим продления, устанавливаем начальную дату на следующий день после окончания
  useEffect(() => {
    if (isExtending && booking) {
      const nextDay = new Date(booking.end_date);
      nextDay.setDate(nextDay.getDate() + 1);

      const endDay = new Date(nextDay);
      endDay.setDate(endDay.getDate() + 1); // По умолчанию 1 день

      setFormData({
        start_date: nextDay,
        end_date: endDay,
        guest_name: booking.guest_name || '',
        notes: booking.notes ? `${booking.notes} (davomi)` : 'Davomi'
      });
    }
  }, [isExtending, booking]);

  const handleSubmit = (e) => {
    e.preventDefault();

    // Проверяем даты
    if (formData.end_date < formData.start_date) {
      alert('Chiqish sanasi kirish sanasidan keyin bo\'lishi kerak');
      return;
    }

    const submitData = {
      ...formData,
      room_id: room.id,
      start_date: formData.start_date.toISOString().split('T')[0],
      end_date: formData.end_date.toISOString().split('T')[0]
    };

    console.log('BookingForm submitting:', submitData);
    onSubmit(submitData);
  };

  const handleExtendClick = () => {
    setIsExtending(true);
  };

  const handleCancelExtend = () => {
    setIsExtending(false);
    // Восстанавливаем оригинальные данные
    if (booking) {
      setFormData({
        start_date: new Date(booking.start_date),
        end_date: new Date(booking.end_date),
        guest_name: booking.guest_name || '',
        notes: booking.notes || ''
      });
    }
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

      {isExtending && (
        <div className="bg-blue-50 border border-blue-200 p-3 rounded-lg">
          <p className="text-sm text-blue-800 font-medium">
            Bronni davom ettirish
          </p>
          <p className="text-xs text-blue-600 mt-1">
            Yangi bron avvalgi brondan keyin boshlanadi
          </p>
        </div>
      )}

      <div className="grid grid-cols-2 gap-4">
        <DatePicker
          label="Kirish sanasi"
          selected={formData.start_date}
          onChange={(date) => setFormData({ ...formData, start_date: date })}
          minDate={isExtending ? formData.start_date : new Date()}
          disabled={isExtending}
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
        <Button
          type="submit"
          className="flex-1"
          loading={isLoading}
        >
          {isExtending ? 'Davom ettirish' : (booking ? 'Yangilash' : 'Saqlash')}
        </Button>

        {booking && !isExtending && (
          <>
            <Button
              type="button"
              variant="secondary"
              onClick={handleExtendClick}
              title="Bronni davom ettirish"
            >
              <ArrowRightIcon className="h-4 w-4" />
            </Button>

            {onDelete && (
              <Button
                type="button"
                variant="danger"
                onClick={onDelete}
                title="Bronni o'chirish"
              >
                <TrashIcon className="h-4 w-4" />
              </Button>
            )}
          </>
        )}

        <Button
          type="button"
          variant="secondary"
          onClick={isExtending ? handleCancelExtend : onCancel}
        >
          Bekor qilish
        </Button>
      </div>
    </form>
  );
}