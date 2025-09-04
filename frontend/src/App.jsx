import React, { useState, useEffect } from 'react';
import { QueryClient, QueryClientProvider } from 'react-query';
import { Toaster } from 'react-hot-toast';
import toast from 'react-hot-toast';
import { LanguageProvider } from './contexts/LanguageContext';

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

      // Временно используем тестового админа для разработки
      const mockUser = {
        id: 1,
        telegram_id: 5488749868,
        first_name: 'Admin',
        last_name: 'Test',
        username: 'admin',
        is_admin: true,
        can_modify: true,
        role: 'admin'
      };

      setCurrentUser(mockUser);
      localStorage.setItem('current_user', JSON.stringify(mockUser));
      localStorage.setItem('auth_token', 'dev_token_' + Date.now());

      toast.success(`Xush kelibsiz, ${mockUser.first_name}!`);

    } catch (error) {
      console.error('Authentication error:', error);
      toast.error('Autentifikatsiya xatosi');
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

  const handleLogout = () => {
    localStorage.clear();
    window.location.reload();
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4">Yuklanmoqda...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header currentUser={currentUser} onLogout={handleLogout} />
      <Navigation activeTab={activeTab} onChange={setActiveTab} />

      <main className="container mx-auto px-4 py-6">
        {currentUser && !currentUser.is_admin && !currentUser.can_modify && (
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

export default App;