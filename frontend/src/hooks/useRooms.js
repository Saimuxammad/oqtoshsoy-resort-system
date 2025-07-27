// useRooms.js
import { useState, useEffect } from 'react';
import { roomService } from '../services/roomService';

export const useRooms = () => {
  const [rooms, setRooms] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchRooms = async () => {
      try {
        const data = await roomService.getRooms();
        setRooms(data);
      } catch (err) {
        console.error('⚠️ Ошибка при загрузке комнат:', err);
        setError(err);
      }
    };

    fetchRooms();
  }, []);

  return { rooms, error };
};
