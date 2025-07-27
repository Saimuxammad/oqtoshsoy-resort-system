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
import { authService } from './services/authService';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      // Добавляем стандартную обработку ошибок
      onError: (error) => {
        console.error('Query error:', error);
      }
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

  useEffect(() => {
    const initAuth = async () => {
      console.log('Initializing auth...');

      try {
        // Проверяем, есть ли уже токен
        if (authService.isAuthenticated()) {
          console.log('Already authenticated');
          setIsAuthenticated(true);
          setIsLoading(false);
          return;
        }

        // Пытаемся авторизоваться
        const authData = await authService.authenticate(
          window.Telegram?.WebApp?.initData || ''
        );

        console.log('Auth successful:', authData);
        setIsAuthenticated(true);
      } catch (error) {
        console.error('Auth failed:', error);
        // Даже если авторизация не удалась, позволяем использовать приложение
        setIsAuthenticated(true);
      } finally {
        setIsLoading(false);
      }
    };

    initAuth();
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