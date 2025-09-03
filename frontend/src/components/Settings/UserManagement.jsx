import React, { useState, useEffect } from 'react';
import { Card, CardContent } from '../UI/Card';
import { Button } from '../UI/Button';
import { Loading } from '../UI/Loading';
import {
  UserIcon,
  ShieldCheckIcon,
  TrashIcon,
  PencilIcon,
  UserPlusIcon,
  CheckIcon,
  XMarkIcon
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';
import api from '../../services/api';

export function UserManagement() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editingUser, setEditingUser] = useState(null);
  const [newUser, setNewUser] = useState({
    telegram_id: '',
    first_name: '',
    last_name: '',
    username: '',
    role: 'OPERATOR'
  });
  const [showAddForm, setShowAddForm] = useState(false);

  // Роли пользователей
  const roles = {
    SUPER_ADMIN: {
      name: 'Super Admin',
      color: 'bg-red-100 text-red-800',
      permissions: 'Barcha huquqlar'
    },
    ADMIN: {
      name: 'Administrator',
      color: 'bg-purple-100 text-purple-800',
      permissions: 'Tizimni boshqarish'
    },
    MANAGER: {
      name: 'Menejer',
      color: 'bg-blue-100 text-blue-800',
      permissions: 'Bronlarni boshqarish'
    },
    OPERATOR: {
      name: 'Operator',
      color: 'bg-green-100 text-green-800',
      permissions: 'Bronlarni ko\'rish va yaratish'
    }
  };

  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    try {
      setLoading(true);
      const response = await api.get('/users');
      setUsers(response.data);
    } catch (error) {
      console.error('Error loading users:', error);
      // Временные данные для демонстрации
      setUsers([
        {
          id: 1,
          telegram_id: '123456789',
          first_name: 'Admin',
          last_name: 'User',
          username: 'admin',
          role: 'SUPER_ADMIN',
          is_active: true,
          created_at: '2025-01-01T00:00:00'
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleRoleChange = async (userId, newRole) => {
    try {
      await api.patch(`/users/${userId}/role`, { role: newRole });
      setUsers(users.map(user =>
        user.id === userId ? { ...user, role: newRole } : user
      ));
      toast.success('Foydalanuvchi roli yangilandi');
    } catch (error) {
      console.error('Error updating role:', error);
      toast.error('Rolni yangilashda xatolik');
    }
  };

  const handleToggleActive = async (userId, currentStatus) => {
    try {
      await api.patch(`/users/${userId}/status`, { is_active: !currentStatus });
      setUsers(users.map(user =>
        user.id === userId ? { ...user, is_active: !currentStatus } : user
      ));
      toast.success(currentStatus ? 'Foydalanuvchi bloklandi' : 'Foydalanuvchi aktivlashtirildi');
    } catch (error) {
      console.error('Error toggling status:', error);
      toast.error('Statusni o\'zgartirishda xatolik');
    }
  };

  const handleDeleteUser = async (userId) => {
    if (!window.confirm('Foydalanuvchini o\'chirishni tasdiqlaysizmi?')) return;

    try {
      await api.delete(`/users/${userId}`);
      setUsers(users.filter(user => user.id !== userId));
      toast.success('Foydalanuvchi o\'chirildi');
    } catch (error) {
      console.error('Error deleting user:', error);
      toast.error('Foydalanuvchini o\'chirishda xatolik');
    }
  };

  const handleAddUser = async () => {
    try {
      const response = await api.post('/users', newUser);
      setUsers([...users, response.data]);
      setNewUser({
        telegram_id: '',
        first_name: '',
        last_name: '',
        username: '',
        role: 'OPERATOR'
      });
      setShowAddForm(false);
      toast.success('Foydalanuvchi qo\'shildi');
    } catch (error) {
      console.error('Error adding user:', error);
      toast.error('Foydalanuvchi qo\'shishda xatolik');
    }
  };

  if (loading) return <Loading />;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <UserIcon className="h-6 w-6 text-gray-600" />
          <h3 className="text-lg font-semibold">Foydalanuvchilarni boshqarish</h3>
        </div>
        <Button
          onClick={() => setShowAddForm(true)}
          variant="primary"
          size="sm"
        >
          <UserPlusIcon className="h-4 w-4 mr-2" />
          Yangi foydalanuvchi
        </Button>
      </div>

      {/* Add User Form */}
      {showAddForm && (
        <Card>
          <CardContent className="p-4">
            <h4 className="font-medium mb-4">Yangi foydalanuvchi qo'shish</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Telegram ID
                </label>
                <input
                  type="text"
                  value={newUser.telegram_id}
                  onChange={(e) => setNewUser({ ...newUser, telegram_id: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="123456789"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Username
                </label>
                <input
                  type="text"
                  value={newUser.username}
                  onChange={(e) => setNewUser({ ...newUser, username: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="@username"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Ism
                </label>
                <input
                  type="text"
                  value={newUser.first_name}
                  onChange={(e) => setNewUser({ ...newUser, first_name: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Familiya
                </label>
                <input
                  type="text"
                  value={newUser.last_name}
                  onChange={(e) => setNewUser({ ...newUser, last_name: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Rol
                </label>
                <select
                  value={newUser.role}
                  onChange={(e) => setNewUser({ ...newUser, role: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {Object.entries(roles).map(([key, role]) => (
                    <option key={key} value={key}>{role.name}</option>
                  ))}
                </select>
              </div>
            </div>
            <div className="flex justify-end gap-2 mt-4">
              <Button
                variant="secondary"
                size="sm"
                onClick={() => setShowAddForm(false)}
              >
                Bekor qilish
              </Button>
              <Button
                variant="primary"
                size="sm"
                onClick={handleAddUser}
              >
                Qo'shish
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Users List */}
      <div className="space-y-4">
        {users.map(user => (
          <Card key={user.id}>
            <CardContent className="p-4">
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-4">
                  <div className="w-12 h-12 bg-gray-200 rounded-full flex items-center justify-center">
                    <UserIcon className="h-6 w-6 text-gray-600" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <h4 className="font-medium text-gray-900">
                        {user.first_name} {user.last_name}
                      </h4>
                      {user.username && (
                        <span className="text-sm text-gray-500">@{user.username}</span>
                      )}
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${roles[user.role]?.color || 'bg-gray-100 text-gray-800'}`}>
                        {roles[user.role]?.name || user.role}
                      </span>
                      {!user.is_active && (
                        <span className="px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
                          Bloklangan
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-gray-600">
                      Telegram ID: {user.telegram_id}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      Huquqlar: {roles[user.role]?.permissions}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  {/* Role selector */}
                  <select
                    value={user.role}
                    onChange={(e) => handleRoleChange(user.id, e.target.value)}
                    className="text-sm px-2 py-1 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    disabled={user.role === 'SUPER_ADMIN'}
                  >
                    {Object.entries(roles).map(([key, role]) => (
                      <option key={key} value={key}>{role.name}</option>
                    ))}
                  </select>

                  {/* Toggle active status */}
                  <Button
                    variant={user.is_active ? 'secondary' : 'success'}
                    size="sm"
                    onClick={() => handleToggleActive(user.id, user.is_active)}
                    title={user.is_active ? 'Bloklash' : 'Aktivlashtirish'}
                  >
                    {user.is_active ? (
                      <XMarkIcon className="h-4 w-4" />
                    ) : (
                      <CheckIcon className="h-4 w-4" />
                    )}
                  </Button>

                  {/* Delete user */}
                  {user.role !== 'SUPER_ADMIN' && (
                    <Button
                      variant="danger"
                      size="sm"
                      onClick={() => handleDeleteUser(user.id)}
                      title="O'chirish"
                    >
                      <TrashIcon className="h-4 w-4" />
                    </Button>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Permissions Table */}
      <Card>
        <CardContent className="p-6">
          <h4 className="font-medium mb-4">Rollar va huquqlar</h4>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Rol</th>
                  <th className="px-4 py-2 text-center text-xs font-medium text-gray-500 uppercase">Bronlash</th>
                  <th className="px-4 py-2 text-center text-xs font-medium text-gray-500 uppercase">Tahrirlash</th>
                  <th className="px-4 py-2 text-center text-xs font-medium text-gray-500 uppercase">O'chirish</th>
                  <th className="px-4 py-2 text-center text-xs font-medium text-gray-500 uppercase">Tahlil</th>
                  <th className="px-4 py-2 text-center text-xs font-medium text-gray-500 uppercase">Sozlamalar</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                <tr>
                  <td className="px-4 py-2 text-sm font-medium">Super Admin</td>
                  <td className="px-4 py-2 text-center">✅</td>
                  <td className="px-4 py-2 text-center">✅</td>
                  <td className="px-4 py-2 text-center">✅</td>
                  <td className="px-4 py-2 text-center">✅</td>
                  <td className="px-4 py-2 text-center">✅</td>
                </tr>
                <tr>
                  <td className="px-4 py-2 text-sm font-medium">Administrator</td>
                  <td className="px-4 py-2 text-center">✅</td>
                  <td className="px-4 py-2 text-center">✅</td>
                  <td className="px-4 py-2 text-center">✅</td>
                  <td className="px-4 py-2 text-center">✅</td>
                  <td className="px-4 py-2 text-center">❌</td>
                </tr>
                <tr>
                  <td className="px-4 py-2 text-sm font-medium">Menejer</td>
                  <td className="px-4 py-2 text-center">✅</td>
                  <td className="px-4 py-2 text-center">✅</td>
                  <td className="px-4 py-2 text-center">⚠️</td>
                  <td className="px-4 py-2 text-center">✅</td>
                  <td className="px-4 py-2 text-center">❌</td>
                </tr>
                <tr>
                  <td className="px-4 py-2 text-sm font-medium">Operator</td>
                  <td className="px-4 py-2 text-center">✅</td>
                  <td className="px-4 py-2 text-center">❌</td>
                  <td className="px-4 py-2 text-center">❌</td>
                  <td className="px-4 py-2 text-center">❌</td>
                  <td className="px-4 py-2 text-center">❌</td>
                </tr>
              </tbody>
            </table>
            <p className="text-xs text-gray-500 mt-2">
              ⚠️ - Faqat o'z bronlarini o'chirish mumkin
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}