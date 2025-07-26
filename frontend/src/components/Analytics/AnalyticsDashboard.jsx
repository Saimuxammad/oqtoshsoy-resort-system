import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { Card, CardHeader, CardContent } from '../UI/Card';
import { Button } from '../UI/Button';
import { Loading } from '../UI/Loading';
import { useLanguage } from '../../contexts/LanguageContext';
import { analyticsService } from '../../services/analyticsService';
import {
  ChartBarIcon,
  ArrowTrendingUpIcon,
  CalendarDaysIcon,
  ArrowDownTrayIcon
} from '@heroicons/react/24/outline';
import { Line, Bar, Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

export function AnalyticsDashboard() {
  const { t } = useLanguage();
  const [dateRange, setDateRange] = useState({
    start: new Date(new Date().setDate(new Date().getDate() - 30)),
    end: new Date()
  });

  const { data: occupancyStats, isLoading: occupancyLoading } = useQuery(
    ['analytics', 'occupancy', dateRange],
    () => analyticsService.getOccupancyStats(dateRange.start, dateRange.end)
  );

  const { data: roomTypeStats } = useQuery(
    ['analytics', 'roomTypes', dateRange],
    () => analyticsService.getRoomTypeStats(dateRange.start, dateRange.end)
  );

  const { data: trends } = useQuery(
    ['analytics', 'trends'],
    () => analyticsService.getBookingTrends(6)
  );

  const handleExport = async () => {
    const response = await analyticsService.exportAnalytics(dateRange.start, dateRange.end);
    const blob = new Blob([response], {
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `analytics_${dateRange.start.toISOString().split('T')[0]}_${dateRange.end.toISOString().split('T')[0]}.xlsx`;
    a.click();
  };

  if (occupancyLoading) return <Loading />;

  // Prepare chart data
  const occupancyChartData = {
    labels: occupancyStats?.daily_stats?.map(stat =>
      new Date(stat.date).toLocaleDateString()
    ) || [],
    datasets: [{
      label: t('occupancyStats'),
      data: occupancyStats?.daily_stats?.map(stat => stat.occupancy_rate) || [],
      borderColor: 'rgb(59, 130, 246)',
      backgroundColor: 'rgba(59, 130, 246, 0.1)',
      tension: 0.3
    }]
  };

  const roomTypeChartData = {
    labels: roomTypeStats?.map(stat => stat.room_type) || [],
    datasets: [{
      label: t('occupancyStats'),
      data: roomTypeStats?.map(stat => stat.occupancy_rate) || [],
      backgroundColor: [
        'rgba(255, 99, 132, 0.5)',
        'rgba(54, 162, 235, 0.5)',
        'rgba(255, 206, 86, 0.5)',
        'rgba(75, 192, 192, 0.5)',
        'rgba(153, 102, 255, 0.5)',
        'rgba(255, 159, 64, 0.5)',
      ]
    }]
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-semibold text-gray-900">{t('analytics')}</h2>
        <Button onClick={handleExport} variant="secondary">
          <ArrowDownTrayIcon className="h-4 w-4 mr-2" />
          {t('exportExcel')}
        </Button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">{t('averageOccupancy')}</p>
                <p className="text-3xl font-semibold text-gray-900">
                  {occupancyStats?.average_occupancy?.toFixed(1) || '0.0'}%
                </p>
              </div>
              <ChartBarIcon className="h-8 w-8 text-primary-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">{t('totalRevenue')}</p>
                <p className="text-3xl font-semibold text-gray-900">
                  {(12500000).toLocaleString()} UZS
                </p>
              </div>
              <ArrowTrendingUpIcon className="h-8 w-8 text-green-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">{t('occupied')}</p>
                <p className="text-3xl font-semibold text-gray-900">
                  {occupancyStats?.daily_stats?.[occupancyStats.daily_stats.length - 1]?.occupied || 0}
                </p>
              </div>
              <CalendarDaysIcon className="h-8 w-8 text-red-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <h3 className="text-lg font-medium">{t('dailyStats')}</h3>
          </CardHeader>
          <CardContent>
            <Line data={occupancyChartData} options={{
              responsive: true,
              plugins: {
                legend: { display: false }
              },
              scales: {
                y: {
                  beginAtZero: true,
                  max: 100
                }
              }
            }} />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <h3 className="text-lg font-medium">{t('roomTypeStats')}</h3>
          </CardHeader>
          <CardContent>
            <Doughnut data={roomTypeChartData} options={{
              responsive: true,
              plugins: {
                legend: { position: 'bottom' }
              }
            }} />
          </CardContent>
        </Card>
      </div>

      {/* Trends */}
      {trends && (
        <Card>
          <CardHeader>
            <h3 className="text-lg font-medium">{t('trends')}</h3>
          </CardHeader>
          <CardContent>
            <Bar data={{
              labels: trends.map(t => t.month),
              datasets: [{
                label: t('bookings'),
                data: trends.map(t => t.bookings_count),
                backgroundColor: 'rgba(59, 130, 246, 0.5)'
              }]
            }} options={{
              responsive: true,
              plugins: {
                legend: { display: false }
              }
            }} />
          </CardContent>
        </Card>
      )}
    </div>
  );
}