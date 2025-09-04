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

      // ВРЕМЕННОЕ РЕШЕНИЕ - устанавливаем админа для тестирования
      // Это позволит приложению работать пока настраиваем Telegram авторизацию
      const mockUser = {
        id: 1,
        telegram_id: 5488749868,
        first_name: 'Admin',
        last_name: 'User',
        username: 'admin',
        is_admin: true,
        can_modify: true,
        role: 'admin'
      };

      setCurrentUser(mockUser);
      localStorage.setItem('current_user', JSON.stringify(mockUser));
      localStorage.setItem('auth_token', 'dev_token_' + Date.now());

      toast.success(`Xush kelibsiz, ${mockUser.first_name}! (Administrator)`);

      /* ЗАКОММЕНТИРОВАНО ДЛЯ ТЕСТИРОВАНИЯ - раскомментируйте когда настроите Telegram
      // Получаем Telegram WebApp данные
      const tg = window.Telegram?.WebApp;
      let authData = null;

      if (tg && tg.initData) {
        authData = tg.initData;
        tg.ready();
        tg.expand();
      }

      // Аутентификация через Telegram
      const result = await authService.authenticate(authData);

      if (result && result.user) {
        setCurrentUser(result.user);
        localStorage.setItem('current_user', JSON.stringify(result.user));

        if (result.user.is_admin) {
          toast.success(`Xush kelibsiz, ${result.user.first_name}! (Administrator)`);
        } else {
          toast.success(`Xush kelibsiz, ${result.user.first_name}! (Faqat ko'rish)`);
        }
      }
      */

    } catch (error) {
      console.error('Authentication error:', error);

      // При ошибке тоже устанавливаем тестового пользователя
      const fallbackUser = {
        id: 1,
        telegram_id: 5488749868,
        first_name: 'Test',
        last_name: 'Admin',
        username: 'testadmin',
        is_admin: true,
        can_modify: true,
        role: 'admin'
      };

      setCurrentUser(fallbackUser);
      localStorage.setItem('current_user', JSON.stringify(fallbackUser));
      toast.error('Telegram auth xatosi, test rejimda ishlamoqda');

    } finally {
      setIsLoading(false);
    }
  };

  const handleEditRoom = (room) => {
    if (!currentUser?.is_admin && !currentUser?.can_modify) {
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

  // Если нет пользователя, показываем сообщение
  if (!currentUser) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Kirish talab qilinadi</h2>
          <p className="text-gray-600 mb-4">Iltimos, sahifani qayta yuklang</p>
          <button
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Qayta yuklash
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header currentUser={currentUser} />
      <Navigation activeTab={activeTab} onChange={setActiveTab} />

      <main className="container mx-auto px-4 py-6">
        {/* Показываем уведомление о правах доступа */}
        {currentUser && !currentUser.is_admin && !currentUser.can_modify && (
          <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
            <p className="text-sm text-yellow-800">
              ⚠️ Sizda faqat ko'rish huquqi mavjud. O'zgartirish uchun administrator bilan bog'laning.
            </p>
          </div>
        )}

        {/* Режим разработки индикатор */}
        {currentUser && currentUser.telegram_id === 5488749868 && (
          <div className="mb-4 p-2 bg-green-50 border border-green-200 rounded-lg">
            <p className="text-xs text-green-800">
              🔧 Test rejimi: Admin sifatida kirilgan (ID: {currentUser.telegram_id})
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

      {(currentUser?.is_admin || currentUser?.can_modify) && (
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