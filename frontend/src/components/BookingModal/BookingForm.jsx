import React, { useState, useEffect } from 'react';
import { Button } from '../UI/Button';
import { format } from 'date-fns';
import toast from 'react-hot-toast';
import { bookingService } from '../../services/bookingService';

export function BookingForm({ room, booking, onSubmit, onCancel, onDelete, isLoading }) {
  const [formData, setFormData] = useState({
    room_id: room?.id || '',
    start_date: booking?.start_date || '',
    end_date: booking?.end_date || '',
    guest_name: booking?.guest_name || '',
    notes: booking?.notes || ''
  });

  const [isChecking, setIsChecking] = useState(false);

  useEffect(() => {
    if (room) {
      setFormData(prev => ({ ...prev, room_id: room.id }));
    }
  }, [room]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const checkAvailability = async () => {
    if (!formData.start_date || !formData.end_date) {
      return true; // Пропускаем проверку если даты не выбраны
    }

    try {
      setIsChecking(true);
      const result = await bookingService.checkAvailability(
        formData.room_id,
        formData.start_date,
        formData.end_date,
        booking?.id // Исключаем текущее бронирование при редактировании
      );

      console.log('Availability check result:', result);
      return result.available;
    } catch (error) {
      console.error('Availability check error:', error);
      // При ошибке проверки разрешаем отправку на сервер
      // Сервер сам проверит и вернет ошибку если нужно
      return true;
    } finally {
      setIsChecking(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Валидация
    if (!formData.start_date || !formData.end_date) {
      toast.error('Sanalarni tanlang');
      return;
    }

    if (new Date(formData.end_date) <= new Date(formData.start_date)) {
      toast.error('Tugash sanasi boshlanish sanasidan keyin bo\'lishi kerak');
      return;
    }

    // Отправляем данные без проверки доступности
    // Сервер сам проверит с правильной логикой
    console.log('[BookingForm] Submitting:', formData);
    onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Xona
        </label>
        <input
          type="text"
          value={`№${room?.room_number} - ${room?.room_type}`}
          disabled
          className="w-full px-3 py-2 border rounded-lg bg-gray-50"
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Kirish sanasi
          </label>
          <input
            type="date"
            name="start_date"
            value={formData.start_date}
            onChange={handleChange}
            min={format(new Date(), 'yyyy-MM-dd')}
            required
            className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Chiqish sanasi
          </label>
          <input
            type="date"
            name="end_date"
            value={formData.end_date}
            onChange={handleChange}
            min={formData.start_date || format(new Date(), 'yyyy-MM-dd')}
            required
            className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Mehmon ismi
        </label>
        <input
          type="text"
          name="guest_name"
          value={formData.guest_name}
          onChange={handleChange}
          placeholder="Mehmon ismi (ixtiyoriy)"
          className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Izohlar
        </label>
        <textarea
          name="notes"
          value={formData.notes}
          onChange={handleChange}
          rows={3}
          placeholder="Qo'shimcha ma'lumotlar (ixtiyoriy)"
          className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 text-sm text-blue-800">
        <p className="font-medium mb-1">Eslatma:</p>
        <ul className="list-disc list-inside space-y-1 text-xs">
          <li>Kirish vaqti: 14:00</li>
          <li>Chiqish vaqti: 12:00</li>
          <li>Bir kunda chiqish va kirish mumkin</li>
        </ul>
      </div>

      <div className="flex justify-between gap-3">
        <div className="flex gap-3">
          {booking && onDelete && (
            <Button
              type="button"
              variant="danger"
              onClick={onDelete}
              disabled={isLoading}
            >
              O'chirish
            </Button>
          )}
        </div>

        <div className="flex gap-3">
          <Button
            type="button"
            variant="secondary"
            onClick={onCancel}
            disabled={isLoading || isChecking}
          >
            Bekor qilish
          </Button>
          <Button
            type="submit"
            loading={isLoading || isChecking}
            disabled={isLoading || isChecking}
          >
            {isChecking ? 'Tekshirilmoqda...' : (booking ? 'Yangilash' : 'Saqlash')}
          </Button>
        </div>
      </div>
    </form>
  );
}