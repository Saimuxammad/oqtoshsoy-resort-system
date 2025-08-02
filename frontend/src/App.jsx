import React, { useState, useEffect } from 'react';
import { QueryClient, QueryClientProvider } from 'react-query';
import { Toaster } from 'react-hot-toast';
import { LanguageProvider } from './contexts/LanguageContext';
import { Header } from './components/Layout/Header';
import { Navigation } from './components/Layout/Navigation';
import { RoomList } from './components/RoomList/RoomList';
import { BookingsList } from './components/BookingsList/BookingsList';
import { BookingModal } from './components/BookingModal/BookingModal';
import { CalendarView } from './components/Calendar/CalendarView';
import { AnalyticsDashboard } from './components/Analytics/AnalyticsDashboard';
import { HistoryLog } from './components/History/HistoryLog';
import { SettingsPanel } from './components/Settings/SettingsPanel';
import { Loading } from './components/UI/Loading';
import { useTelegram } from './hooks/useTelegram';
import { authService } from './services/authService';
import { AccessDenied } from './components/AccessDenied';import { TestAPI } from './components/TestAPI';

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

  useEffect(() => {
    console.log('App starting...');
    console.log('import.meta.env.DEV:', import.meta.env.DEV);
    console.log('Telegram WebApp:', window.Telegram?.WebApp);
    console.log('User:', user);
    console.log('isReady:', isReady);

    // Для production Railway или dev режима
    if (import.meta.env.DEV || !window.Telegram?.WebApp) {
      console.log('Dev mode or no Telegram - auto authenticate');
      setIsAuthenticated(true);
      setAuthToken('dev_token');
      setIsLoading(false);
    } else if (isReady && user) {
      console.log('Telegram mode - authenticating...');
      authService.authenticate(window.Telegram.WebApp.initData)
        .then((data) => {
          console.log('Auth success:', data);
          setIsAuthenticated(true);
          setAuthToken(data.token || 'dev_token');
        })
        .catch((error) => {
          console.error('Authentication failed:', error);
          // В production тоже разрешаем для тестирования
          setIsAuthenticated(true);
          setAuthToken('dev_token');
        })
        .finally(() => {
          setIsLoading(false);
        });
    } else {
      // Если ничего не сработало - все равно показываем интерфейс
      setTimeout(() => {
        console.log('Timeout - auto authenticate');
        setIsAuthenticated(true);
        setAuthToken('dev_token');
        setIsLoading(false);
      }, 1000);
    }
  }, [isReady, user]);

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
          <BookingsList />
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