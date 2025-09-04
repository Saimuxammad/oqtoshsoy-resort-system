// frontend/src/components/Auth/SimpleLogin.jsx
import React, { useState } from 'react';
import { Button } from '../UI/Button';
import toast from 'react-hot-toast';

export function SimpleLogin({ onLogin }) {
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const response = await fetch('https://oqtoshsoy-resort-system-production-ef7c.up.railway.app/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ password })
      });

      if (!response.ok) {
        throw new Error('Noto\'g\'ri parol');
      }

      const data = await response.json();

      // Сохраняем токен
      localStorage.setItem('auth_token', data.token);
      localStorage.setItem('user', JSON.stringify(data.user));

      toast.success('Muvaffaqiyatli kirdingiz!');
      onLogin(data);

    } catch (error) {
      toast.error(error.message || 'Xatolik yuz berdi');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-2xl p-8 w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-2xl font-bold text-gray-800">Oqtoshsoy Resort</h1>
          <p className="text-gray-600 mt-2">Administrator kirishi</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Parol
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Parolni kiriting"
              autoFocus
            />
          </div>

          <Button type="submit" loading={isLoading} className="w-full">
            Kirish
          </Button>
        </form>

        <div className="mt-6 p-4 bg-yellow-50 rounded-lg">
          <p className="text-sm text-yellow-800">
            ⚠️ Faqat ruxsat berilgan shaxslar kira oladi
          </p>
        </div>
      </div>
    </div>
  );
}