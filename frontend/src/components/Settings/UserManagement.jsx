import React, { useState, useEffect } from 'react';
import { Card, CardContent } from '../UI/Card';
import { Button } from '../UI/Button';
import { Loading } from '../UI/Loading';
import {
  UserIcon,
  ShieldCheckIcon,
  PencilIcon,
  TrashIcon,
  UserPlusIcon
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';
import api from '../../services/api';

export function UserManagement({ currentUser }) {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editingUser, setEditingUser] = useState(null);
  const [showAddUser, setShowAddUser] = useState(false);

  // Проверка прав доступа
  const canManageUsers = currentUser?.role === 'super_admin' || currentUser?.role === 'SUPER_ADMIN';

  useEffect(() => {
    if (canManageUsers) {
      loadUsers();
    } else {
      setLoading(false);
    }
  }, [canManageUsers]);

  const loadUsers = async () => {
    try {
      setLoading(true);
      const response = await api.get('/users');
      setUsers(response.data || []);
    } catch (error) {
      console.error('Error loading users:', error);
      toast.error('Foydalanuvchilarni yuklashda xatolik');
      setUsers([]);
    } finally {
      setLoading(false);
    }
  };

  const handleRoleChange = async (userId, newRole) => {
    try {
      await api.patch(`/users/${userId}/role`, { role: newRole });
      toast.success('Rol muvaffaqiyatli o\'zgartirildi');
      loadUsers();
    } catch (error) {
      console.error('Error changing role:', error);
      toast.error('Rolni o\'zgartirishda xatolik');
    }
  };

  const handleToggleActive = async (userId, isActive) => {
    try {
      await api.patch(`/users/${userId}/status`, { is_active: !isActive });
      toast.success(isActive ? 'Foydalanuvchi bloklandi' : 'Foydalanuvchi aktivlashtirildi');
      loadUsers();
    } catch (error) {
      console.error('Error toggling user status:', error);
      toast.error('Statusni o\'zgartirishda xatolik');
    }
  };

  const roles = [
    { value: 'user', label: 'Foydalanuvchi', color: 'bg-gray-100 text-gray-800' },
    { value: 'operator', label: 'Operator', color: 'bg-blue-100 text-blue-800' },
    { value: 'manager', label: 'Menejer', color: 'bg-green-100 text-green-800' },
    { value: 'admin', label: 'Administrator', color: 'bg-purple-100 text-purple-800' },
    { value: 'super_admin', label: 'Super Admin', color: 'bg-red-100 text-red-800' }
  ];

  const getRoleInfo = (role) => {
    const roleStr = String(role).toLowerCase();
    return roles.find(r => r.value === roleStr) || roles[0];
  };

  if (loading) return <Loading />;

  if (!canManageUsers) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="text-center py-8">
            <ShieldCheckIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600">Foydalanuvchilarni boshqarish uchun Super Admin huquqlari kerak</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardContent className="p-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center">
            <UserIcon className="h-6 w-6 mr-2 text-gray-600" />
            <h3 className="text-lg font-semibold">Foydalanuvchilarni boshqarish</h3>
          </div>
          <span className="text-sm text-gray-500">
            Jami: {users.length} foydalanuvchi
          </span>
        </div>

        <div className="space-y-4">
          {/* Таблица пользователей */}
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Foydalanuvchi
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Telegram ID
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Rol
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Huquqlar
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Amallar
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {users.map((user) => {
                  const roleInfo = getRoleInfo(user.role);
                  const isCurrentUser = user.telegram_id === currentUser?.telegram_id;

                  return (
                    <tr key={user.id} className={isCurrentUser ? 'bg-blue-50' : ''}>
                      <td className="px-4 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div>
                            <div className="text-sm font-medium text-gray-900">
                              {user.first_name} {user.last_name}
                              {isCurrentUser && (
                                <span className="ml-2 text-xs text-blue-600">(Siz)</span>
                              )}
                            </div>
                            {user.username && (
                              <div className="text-sm text-gray-500">@{user.username}</div>
                            )}
                          </div>
                        </div>
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-500">
                        {user.telegram_id}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap">
                        {editingUser === user.id ? (
                          <select
                            value={user.role.toLowerCase()}
                            onChange={(e) => {
                              handleRoleChange(user.id, e.target.value);
                              setEditingUser(null);
                            }}
                            onBlur={() => setEditingUser(null)}
                            className="text-sm border rounded px-2 py-1"
                            autoFocus
                          >
                            {roles.map(role => (
                              <option key={role.value} value={role.value}>
                                {role.label}
                              </option>
                            ))}
                          </select>
                        ) : (
                          <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${roleInfo.color}`}>
                            {roleInfo.label}
                          </span>
                        )}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                          user.is_active 
                            ? 'bg-green-100 text-green-800' 
                            : 'bg-red-100 text-red-800'
                        }`}>
                          {user.is_active ? 'Faol' : 'Bloklangan'}
                        </span>
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap">
                        <div className="text-xs space-y-1">
                          {user.can_create_bookings && (
                            <span className="block text-green-600">✓ Bron yaratish</span>
                          )}
                          {user.can_edit_bookings && (
                            <span className="block text-green-600">✓ Tahrirlash</span>
                          )}
                          {user.can_delete_any_booking && (
                            <span className="block text-green-600">✓ O'chirish</span>
                          )}
                          {user.can_view_analytics && (
                            <span className="block text-green-600">✓ Tahlil</span>
                          )}
                          {user.can_manage_settings && (
                            <span className="block text-green-600">✓ Sozlamalar</span>
                          )}
                          {user.can_manage_users && (
                            <span className="block text-red-600">✓ Foydalanuvchilar</span>
                          )}
                        </div>
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm">
                        <div className="flex space-x-2">
                          {!isCurrentUser && (
                            <>
                              <button
                                onClick={() => setEditingUser(user.id)}
                                className="text-blue-600 hover:text-blue-900"
                                title="Rolni o'zgartirish"
                              >
                                <PencilIcon className="h-4 w-4" />
                              </button>
                              <button
                                onClick={() => handleToggleActive(user.id, user.is_active)}
                                className={`${
                                  user.is_active 
                                    ? 'text-red-600 hover:text-red-900' 
                                    : 'text-green-600 hover:text-green-900'
                                }`}
                                title={user.is_active ? 'Bloklash' : 'Aktivlashtirish'}
                              >
                                <ShieldCheckIcon className="h-4 w-4" />
                              </button>
                            </>
                          )}
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          {/* Роли и их права */}
          <div className="mt-8 border-t pt-6">
            <h4 className="text-md font-semibold mb-4">Rollar va huquqlar</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <div className="border rounded-lg p-4">
                <h5 className="font-medium text-gray-900 mb-2">👤 Foydalanuvchi</h5>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>• Xonalarni ko'rish</li>
                  <li className="text-gray-400">✗ Bron yaratish</li>
                  <li className="text-gray-400">✗ Tahrirlash</li>
                </ul>
              </div>

              <div className="border rounded-lg p-4">
                <h5 className="font-medium text-blue-900 mb-2">💼 Operator</h5>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>• Xonalarni ko'rish</li>
                  <li>• Bron yaratish</li>
                  <li className="text-gray-400">✗ Tahrirlash/O'chirish</li>
                </ul>
              </div>

              <div className="border rounded-lg p-4">
                <h5 className="font-medium text-green-900 mb-2">📊 Menejer</h5>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>• Bron yaratish/tahrirlash</li>
                  <li>• O'z bronlarini o'chirish</li>
                  <li>• Tahlil va hisobotlar</li>
                </ul>
              </div>

              <div className="border rounded-lg p-4">
                <h5 className="font-medium text-purple-900 mb-2">⚙️ Administrator</h5>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>• Barcha bronlarni boshqarish</li>
                  <li>• Tizim sozlamalari</li>
                  <li className="text-gray-400">✗ Foydalanuvchilar</li>
                </ul>
              </div>

              <div className="border rounded-lg p-4">
                <h5 className="font-medium text-red-900 mb-2">👑 Super Admin</h5>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>• To'liq huquqlar</li>
                  <li>• Foydalanuvchilarni boshqarish</li>
                  <li>• Rollarni o'zgartirish</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}