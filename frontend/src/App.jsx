import React, { useState, useEffect } from 'react';
import { QueryClient, QueryClientProvider } from 'react-query';
import { Toaster } from 'react-hot-toast';
import toast from 'react-hot-toast';

// Компоненты
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

// Сервисы
import { authService } from './services/authService';

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
  const [currentUser, setCurrentUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    authenticateUser();
  }, []);

  const authenticateUser = async () => {
    try {
      setIsLoading(true);

      // Получаем Telegram WebApp данные
      const tg = window.Telegram?.WebApp;
      let authData = null;

      if (tg && tg.initData) {
        authData = tg.initData;
        tg.ready();
        tg.expand();
      }

      // Аутентификация
      const result = await authService.authenticate(authData);

      if (result && result.user) {
        setCurrentUser(result.user);

        // Сохраняем данные пользователя
        localStorage.setItem('current_user', JSON.stringify(result.user));

        // Показываем приветственное сообщение
        if (result.user.is_admin) {
          toast.success(`Xush kelibsiz, ${result.user.first_name}! (Administrator)`);
        } else {
          toast.success(`Xush kelibsiz, ${result.user.first_name}! (Faqat ko'rish)`);
        }
      }
    } catch (error) {
      console.error('Authentication error:', error);
      toast.error('Autentifikatsiya xatosi');
    } finally {
      setIsLoading(false);
    }
  };

  const handleEditRoom = (room) => {
    if (!currentUser?.is_admin) {
      toast.error("Sizda tahrirlash huquqi yo'q");
      return;
    }
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
    return <Loading text="Yuklanmoqda..." />;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header currentUser={currentUser} />
      <Navigation activeTab={activeTab} onChange={setActiveTab} />

      <main className="container mx-auto px-4 py-6">
        {/* Показываем уведомление о правах доступа */}
        {currentUser && !currentUser.is_admin && (
          <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
            <p className="text-sm text-yellow-800">
              ⚠️ Sizda faqat ko'rish huquqi mavjud. O'zgartirish uchun administrator bilan bog'laning.
            </p>
          </div>
        )}

        {activeTab === 'rooms' && (
          <RoomList
            onEditRoom={handleEditRoom}
            onViewCalendar={handleViewCalendar}
            currentUser={currentUser}
          />
        )}

        {activeTab === 'bookings' && (
          <BookingsList currentUser={currentUser} />
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
          <SettingsPanel currentUser={currentUser} />
        )}
      </main>

      {currentUser?.is_admin && (
        <BookingModal
          isOpen={isBookingModalOpen}
          onClose={handleCloseModal}
          room={selectedRoom}
          booking={selectedBooking}
        />
      )}
    </div>
  );
}

function App() {
  return (
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
  );
}

export default App;