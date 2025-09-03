import React, { useState } from 'react';
import { Button } from '../UI/Button';
import toast from 'react-hot-toast';

export function LoginForm({ onLogin }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  // Предустановленные пользователи (в реальном приложении это должно быть на сервере)
  const users = {
    admin: { password: 'admin123', role: 'Administrator', name: 'Admin' },
    manager: { password: 'manager123', role: 'Manager', name: 'Menejer' },
    operator1: { password: 'operator123', role: 'Operator', name: 'Operator 1' },
    operator2: { password: 'operator123', role: 'Operator', name: 'Operator 2' },
    viewer: { password: 'viewer123', role: 'Viewer', name: 'Kuzatuvchi' }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setIsLoading(true);

    setTimeout(() => {
      const user = users[username];

      if (user && user.password === password) {
        const userData = {
          username,
          name: user.name,
          role: user.role,
          permissions: getPermissionsByRole(user.role)
        };

        localStorage.setItem('currentUser', JSON.stringify(userData));
        toast.success(`Xush kelibsiz, ${user.name}!`);
        onLogin(userData);
      } else {
        toast.error('Noto\'g\'ri login yoki parol');
      }

      setIsLoading(false);
    }, 500);
  };

  const getPermissionsByRole = (role) => {
    const permissions = {
      Administrator: ['create', 'read', 'update', 'delete', 'analytics', 'settings'],
      Manager: ['create', 'read', 'update', 'delete', 'analytics'],
      Operator: ['create', 'read', 'update'],
      Viewer: ['read']
    };
    return permissions[role] || ['read'];
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
      <div className="bg-white rounded-lg shadow-2xl p-8 w-full max-w-md">
        <div className="text-center mb-8">
          {/* Logo joyi - public/logo.png faylini qo'shing */}
          <img
            src="/logo.png"
            alt="Oqtoshsoy Resort"
            className="w-24 h-24 mx-auto mb-4"
            onError={(e) => {
              e.target.style.display = 'none';
            }}
          />
          <h1 className="text-2xl font-bold text-gray-800">Oqtoshsoy Resort</h1>
          <p className="text-gray-600">Xonalarni boshqarish tizimi</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Login
            </label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="admin, manager, operator1, viewer..."
            />
          </div>

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
            />
          </div>

          <Button type="submit" loading={isLoading} className="w-full">
            Kirish
          </Button>
        </form>

        <div className="mt-6 p-4 bg-gray-50 rounded-lg">
          <p className="text-sm text-gray-600 font-medium mb-2">Test uchun:</p>
          <div className="text-xs space-y-1 text-gray-500">
            <p>👤 <b>admin</b> / admin123 - To'liq huquq</p>
            <p>👤 <b>manager</b> / manager123 - Boshqaruvchi</p>
            <p>👤 <b>operator1</b> / operator123 - Operator</p>
            <p>👤 <b>viewer</b> / viewer123 - Faqat ko'rish</p>
          </div>
        </div>
      </div>
    </div>
  );
}