import React, { useState, useEffect } from 'react';
import { Card, CardContent } from '../UI/Card';
import { Loading } from '../UI/Loading';
import { ArrowUpIcon, ArrowDownIcon, UsersIcon, HomeIcon, CurrencyDollarIcon, CalendarDaysIcon } from '@heroicons/react/24/outline';
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import api from '../../services/api';

export function AnalyticsDashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAnalytics();
  }, []);

  const loadAnalytics = async () => {
    try {
      setLoading(true);

      // Загружаем данные о комнатах и бронированиях
      const [roomsRes, bookingsRes] = await Promise.all([
        api.get('/rooms'),
        api.get('/bookings')
      ]);

      const rooms = roomsRes.data || [];
      const bookings = bookingsRes.data || [];

      // Считаем статистику
      const today = new Date().toISOString().split('T')[0];
      const occupiedRooms = bookings.filter(b =>
        b.start_date <= today && b.end_date >= today
      ).length;

      // Группируем комнаты по типам
      const roomTypes = {};
      rooms.forEach(room => {
        if (!roomTypes[room.room_type]) {
          roomTypes[room.room_type] = { total: 0, occupied: 0, revenue: 0 };
        }
        roomTypes[room.room_type].total++;
        roomTypes[room.room_type].revenue += room.price_per_night || 0;
      });

      // Считаем занятость по типам
      bookings.forEach(booking => {
        const room = rooms.find(r => r.id === booking.room_id);
        if (room && roomTypes[room.room_type]) {
          if (booking.start_date <= today && booking.end_date >= today) {
            roomTypes[room.room_type].occupied++;
          }
        }
      });

      // Подготовка данных для графиков
      const roomTypeData = Object.entries(roomTypes).map(([type, data]) => ({
        name: type.replace("o'rinli", "o'r"),
        total: data.total,
        band: data.occupied,
        bo'sh: data.total - data.occupied
      }));

      // Данные по месяцам (последние 6 месяцев)
      const monthlyData = [];
      const months = ['Yanvar', 'Fevral', 'Mart', 'Aprel', 'May', 'Iyun', 'Iyul', 'Avgust', 'Sentabr', 'Oktabr', 'Noyabr', 'Dekabr'];
      const currentMonth = new Date().getMonth();

      for (let i = 5; i >= 0; i--) {
        const monthIndex = (currentMonth - i + 12) % 12;
        const monthBookings = bookings.filter(b => {
          const bookingMonth = new Date(b.start_date).getMonth();
          return bookingMonth === monthIndex;
        });

        monthlyData.push({
          name: months[monthIndex].substring(0, 3),
          bronlar: monthBookings.length,
          daromad: monthBookings.length * 500000 // Примерная цена
        });
      }

      setStats({
        totalRooms: rooms.length,
        occupiedRooms,
        occupancyRate: Math.round((occupiedRooms / rooms.length) * 100),
        totalBookings: bookings.length,
        monthlyRevenue: bookings.length * 500000,
        roomTypeData,
        monthlyData
      });

    } catch (error) {
      console.error('Analytics error:', error);
      setStats({
        totalRooms: 0,
        occupiedRooms: 0,
        occupancyRate: 0,
        totalBookings: 0,
        monthlyRevenue: 0,
        roomTypeData: [],
        monthlyData: []
      });
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <Loading />;
  if (!stats) return <div>Ma'lumotlar yuklanmadi</div>;

  const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899'];

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-900">Tahlil va Statistika</h2>

      {/* Asosiy ko'rsatkichlar */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Jami xonalar</p>
                <p className="text-3xl font-bold text-gray-900">{stats.totalRooms}</p>
              </div>
              <HomeIcon className="h-10 w-10 text-blue-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Band xonalar</p>
                <p className="text-3xl font-bold text-gray-900">{stats.occupiedRooms}</p>
                <p className="text-xs text-gray-500 mt-1">{stats.occupancyRate}% bandlik</p>
              </div>
              <UsersIcon className="h-10 w-10 text-green-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Jami bronlar</p>
                <p className="text-3xl font-bold text-gray-900">{stats.totalBookings}</p>
              </div>
              <CalendarDaysIcon className="h-10 w-10 text-purple-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Oylik daromad</p>
                <p className="text-2xl font-bold text-gray-900">
                  {(stats.monthlyRevenue / 1000000).toFixed(1)}M
                </p>
                <p className="text-xs text-gray-500">so'm</p>
              </div>
              <CurrencyDollarIcon className="h-10 w-10 text-yellow-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Grafiklar */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Xonalar bo'yicha statistika */}
        <Card>
          <CardContent className="p-6">
            <h3 className="text-lg font-semibold mb-4">Xonalar holati</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={stats.roomTypeData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" angle={-45} textAnchor="end" height={80} />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="band" fill="#3B82F6" name="Band" />
                <Bar dataKey="bo'sh" fill="#10B981" name="Bo'sh" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Oylik trend */}
        <Card>
          <CardContent className="p-6">
            <h3 className="text-lg font-semibold mb-4">Oylik dinamika</h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={stats.monthlyData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="bronlar" stroke="#8B5CF6" name="Bronlar" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Xona turlari bo'yicha ulush */}
        <Card>
          <CardContent className="p-6">
            <h3 className="text-lg font-semibold mb-4">Xona turlari ulushi</h3>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={stats.roomTypeData}
                  dataKey="total"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  outerRadius={100}
                  label
                >
                  {stats.roomTypeData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Statistika jadvali */}
        <Card>
          <CardContent className="p-6">
            <h3 className="text-lg font-semibold mb-4">Xona turlari statistikasi</h3>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Turi</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Jami</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Band</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Bo'sh</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Bandlik %</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {stats.roomTypeData.map((type, index) => (
                    <tr key={index}>
                      <td className="px-4 py-2 text-sm text-gray-900">{type.name}</td>
                      <td className="px-4 py-2 text-sm text-gray-900">{type.total}</td>
                      <td className="px-4 py-2 text-sm text-gray-900">{type.band}</td>
                      <td className="px-4 py-2 text-sm text-gray-900">{type.bo'sh}</td>
                      <td className="px-4 py-2 text-sm text-gray-900">
                        {type.total > 0 ? Math.round((type.band / type.total) * 100) : 0}%
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}