import React, { useState, useEffect } from 'react';
import { Card, CardContent } from '../UI/Card';
import { Button } from '../UI/Button';
import { UserIcon, ShieldCheckIcon, TrashIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';
import api from '../../services/api';

export function UserManagement() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [currentUser, setCurrentUser] = useState(null);

  const roles = {
    super_admin: { label: 'Super Admin', color: 'bg-purple-100 text-purple-800' },
    admin: { label: 'Administrator', color: 'bg-red-100 text-red-800' },
    manager: { label: 'Menejer', color: 'bg-blue-100 text-blue-800' },
    operator: { label: 'Operator', color: 'bg-green-100 text-green-800' },
    user: { label: 'Foydalanuvchi', color: 'bg-gray-100 text-gray-800' }
  };

  useEffect(() => {
    loadUsers();
    loadCurrentUser();
  }, []);

  const loadCurrentUser = async () => {
    try {
      const response = await api.get('/auth/me');
      setCurrentUser(response.data);
    } catch (error) {
      console.error('Error loading current user:', error);
    }
  };

  const loadUsers = async () => {
    try {
      setLoading(true);
      const response = await api.get('/users');
      setUsers(response.data);
    } catch (error) {
      console.error('Error loading users:', error);
      toast.error('Foydalanuvchilarni yuklashda xatolik');
    } finally {
      setLoading(false);
    }
  };

  const updateUserRole = async (userId, newRole) => {
    try {
      await api.put(`/users/${userId}/role`, { role: newRole });
      toast.success('Rol muvaffaqiyatli o\'zgartirildi');
      loadUsers();
    } catch (error) {
      console.error('Error updating role:', error);
      toast.error('Rolni o\'zgartirishda xatolik');
    }
  };

  const toggleUserStatus = async (userId, currentStatus) => {
    try {
      await api.put(`/users/${userId}/status`, { is_active: !currentStatus });
      toast.success('Foydalanuvchi holati o\'zgartirildi');
      loadUsers();
    } catch (error) {
      console.error('Error toggling status:', error);
      toast.error('Holatni o\'zgartirishda xatolik');
    }
  };

  const deleteUser = async (userId) => {
    if (!window.confirm('Bu foydalanuvchini o\'chirishni xohlaysizmi?')) {
      return;
    }

    try {
      await api.delete(`/users/${userId}`);
      toast.success('Foydalanuvchi o\'chirildi');
      loadUsers();
    } catch (error) {
      console.error('Error deleting user:', error);
      toast.error('Foydalanuvchini o\'chirishda xatolik');
    }
  };

  if (loading) {
    return <div>Yuklanmoqda...</div>;
  }

  // Проверяем права текущего пользователя
  const canManageUsers = currentUser?.role === 'super_admin' || currentUser?.role === 'admin';

  if (!canManageUsers) {
    return (
      <Card>
        <CardContent className="p-6 text-center">
          <ShieldCheckIcon className="h-12 w-12 mx-auto mb-4 text-gray-400" />
          <p className="text-gray-600">Sizda foydalanuvchilarni boshqarish huquqi yo'q</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center mb-4">
            <UserIcon className="h-6 w-6 mr-2 text-gray-600" />
            <h3 className="text-lg font-semibold">Foydalanuvchilarni boshqarish</h3>
          </div>

          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Foydalanuvchi
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Telegram
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Rol
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Holat
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Harakatlar
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {users.map((user) => (
                  <tr key={user.id}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <div className="text-sm font-medium text-gray-900">
                          {user.first_name} {user.last_name}
                        </div>
                        <div className="text-sm text-gray-500">
                          ID: {user.telegram_id}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">
                        @{user.username || 'N/A'}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {currentUser?.role === 'super_admin' && user.id !== currentUser.id ? (
                        <select
                          value={user.role}
                          onChange={(e) => updateUserRole(user.id, e.target.value)}
                          className="text-sm rounded-lg px-3 py-1 border"
                        >
                          {Object.entries(roles).map(([key, value]) => (
                            <option key={key} value={key}>
                              {value.label}
                            </option>
                          ))}
                        </select>
                      ) : (
                        <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${roles[user.role]?.color}`}>
                          {roles[user.role]?.label}
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <button
                        onClick={() => toggleUserStatus(user.id, user.is_active)}
                        className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full cursor-pointer ${
                          user.is_active 
                            ? 'bg-green-100 text-green-800' 
                            : 'bg-red-100 text-red-800'
                        }`}
                        disabled={user.id === currentUser?.id}
                      >
                        {user.is_active ? 'Faol' : 'Nofaol'}
                      </button>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      {currentUser?.role === 'super_admin' && user.id !== currentUser.id && (
                        <button
                          onClick={() => deleteUser(user.id)}
                          className="text-red-600 hover:text-red-900"
                        >
                          <TrashIcon className="h-5 w-5" />
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="p-6">
          <h3 className="text-lg font-semibold mb-4">Rollar va ruxsatlar</h3>

          <div className="space-y-4">
            <div>
              <h4 className="font-medium text-purple-800">Super Admin</h4>
              <p className="text-sm text-gray-600">Barcha huquqlar, tizimni to'liq boshqarish</p>
            </div>

            <div>
              <h4 className="font-medium text-red-800">Administrator</h4>
              <p className="text-sm text-gray-600">Foydalanuvchilarni boshqarish, barcha bronlarni o'chirish va tahrirlash</p>
            </div>

            <div>
              <h4 className="font-medium text-blue-800">Menejer</h4>
              <p className="text-sm text-gray-600">Bronlarni boshqarish, analitika ko'rish, o'z bronlarini o'chirish</p>
            </div>

            <div>
              <h4 className="font-medium text-green-800">Operator</h4>
              <p className="text-sm text-gray-600">Bron yaratish, o'z bronlarini tahrirlash</p>
            </div>

            <div>
              <h4 className="font-medium text-gray-800">Foydalanuvchi</h4>
              <p className="text-sm text-gray-600">Faqat ko'rish va oddiy bron yaratish</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}