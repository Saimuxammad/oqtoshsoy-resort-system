import React, { useState, useEffect } from 'react';
import { QueryClient, QueryClientProvider } from 'react-query';
import { Toaster } from 'react-hot-toast';
import { LanguageProvider } from './contexts/LanguageContext';
import { Header } from './components/Layout/Header';
import { Navigation } from './components/Layout/Navigation';
import { RoomList } from './components/RoomList/RoomList';
import { BookingModal } from './components/BookingModal/BookingModal';
import { CalendarView } from './components/Calendar/CalendarView';
import { AnalyticsDashboard } from './components/Analytics/AnalyticsDashboard';
import { HistoryLog } from './components/History/HistoryLog';
import { SettingsPanel } from './components/Settings/SettingsPanel';
import { Loading } from './components/UI/Loading';
import { useTelegram } from './hooks/useTelegram';
import { useWebSocket } from './hooks/useWebSocket';
import { authService } from './services/authService';
import { RoomList } from './components/RoomList/RoomList';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function AppContent() {
  const [activeTab, setActiveTab] = useState('rooms');
  const [selectedRoom, setSelectedRoom] = useState(null);
  const [isBookingModalOpen, setIsBookingModalOpen] = useState(false);
  const [selectedBooking, setSelectedBooking] = useState(null);

  const { user, isReady } = useTelegram();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [authToken, setAuthToken] = useState(null);

  // WebSocket connection - закомментируем пока
  // useWebSocket(
  //   `${import.meta.env.VITE_WS_URL || 'ws://localhost:8000/api/ws'}`,
  //   authToken
  // );

  useEffect(() => {
    console.log('App starting...');
    console.log('Environment:', import.meta.env.MODE);
    console.log('API URL:', import.meta.env.VITE_API_URL);
    console.log('Telegram WebApp:', window.Telegram?.WebApp);
    console.log('User:', user);
    console.log('isReady:', isReady);

    const initializeAuth = async () => {
      try {
        // Всегда пытаемся аутентифицироваться
        const authData = await authService.authenticate(
          window.Telegram?.WebApp?.initData || ''
        );

        console.log('Auth success:', authData);
        setIsAuthenticated(true);
        setAuthToken(authData.access_token || 'dev_token');
      } catch (error) {
        console.error('Authentication failed:', error);
        // В случае ошибки все равно показываем интерфейс для тестирования
        setIsAuthenticated(true);
        setAuthToken('dev_token');
      } finally {
        setIsLoading(false);
      }
    };

    initializeAuth();
  }, []);

  const handleEditRoom = (room) => {
    setSelectedRoom(room);
    setSelectedBooking(room.current_booking);
    setIsBookingModalOpen(true);
  };

  const handleViewCalendar = (room) => {
    setSelectedRoom(room);
    setActiveTab('calendar');
  };

  const handleCloseModal = () => {
    setIsBookingModalOpen(false);
    setSelectedRoom(null);
    setSelectedBooking(null);
  };

  if (isLoading) {
    return <Loading text="Tizimga ulanmoqda..." />;
  }

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-xl font-semibold text-gray-900 mb-2">
            Ruxsat berilmagan
          </h2>
          <p className="text-gray-600">
            Iltimos, Telegram orqali kiring
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <Navigation activeTab={activeTab} onChange={setActiveTab} />

      <main className="container mx-auto px-4 py-6">
  {activeTab === 'rooms' && (
    <RoomList
      onEditRoom={handleEditRoom}
      onViewCalendar={handleViewCalendar}
    />
  )}

  {activeTab === 'bookings' && (
    <RoomList />
  )}

  {activeTab === 'calendar' && (
    <CalendarView selectedRoom={selectedRoom} />
  )}

  {activeTab === 'analytics' && (
    <AnalyticsDashboard />
  )}

  {activeTab === 'history' && (
    <HistoryLog />
  )}

  {activeTab === 'settings' && (
    <SettingsPanel />
  )}
</main>

      <BookingModal
        isOpen={isBookingModalOpen}
        onClose={handleCloseModal}
        room={selectedRoom}
        booking={selectedBooking}
      />
    </div>
  );
}

export default function App() {
  return (
    <LanguageProvider>
      <QueryClientProvider client={queryClient}>
        <AppContent />
        <Toaster
          position="top-center"
          toastOptions={{
            duration: 3000,
            style: {
              background: '#363636',
              color: '#fff',
            },
          }}
        />
      </QueryClientProvider>
    </LanguageProvider>
  );
}