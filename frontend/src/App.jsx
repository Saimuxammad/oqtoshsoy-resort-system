// Добавьте эту проверку в начало App.jsx после импортов

function AppContent() {
  const [activeTab, setActiveTab] = useState('rooms');
  const [selectedRoom, setSelectedRoom] = useState(null);
  const [isBookingModalOpen, setIsBookingModalOpen] = useState(false);
  const [selectedBooking, setSelectedBooking] = useState(null);
  const [currentUser, setCurrentUser] = useState(null);

  // ... остальные стейты

  useEffect(() => {
    // Проверяем авторизацию
    const savedUser = localStorage.getItem('currentUser');
    if (savedUser) {
      setCurrentUser(JSON.parse(savedUser));
    }
  }, []);

  const handleLogin = (user) => {
    setCurrentUser(user);
  };

  const handleLogout = () => {
    localStorage.removeItem('currentUser');
    setCurrentUser(null);
    toast.success('Tizimdan chiqdingiz');
  };

  // Если не авторизован - показываем форму входа
  if (!currentUser) {
    return <LoginForm onLogin={handleLogin} />;
  }

  // Проверка прав доступа
  const hasPermission = (permission) => {
    return currentUser.permissions.includes(permission);
  };

  // Фильтруем вкладки на основе прав
  const getVisibleTabs = () => {
    const tabs = ['rooms', 'bookings'];

    if (hasPermission('analytics')) tabs.push('analytics');
    tabs.push('history'); // История доступна всем
    if (hasPermission('settings')) tabs.push('settings');

    return tabs;
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header currentUser={currentUser} onLogout={handleLogout} />
      <Navigation
        activeTab={activeTab}
        onChange={setActiveTab}
        visibleTabs={getVisibleTabs()}
        hasPermission={hasPermission}
      />

      <main className="container mx-auto px-4 py-6">
        {/* Контент в зависимости от прав */}
        {activeTab === 'rooms' && (
          <RoomList
            onEditRoom={hasPermission('update') ? handleEditRoom : null}
            onViewCalendar={handleViewCalendar}
            canCreate={hasPermission('create')}
          />
        )}

        {activeTab === 'bookings' && (
          <BookingsList
            canDelete={hasPermission('delete')}
            canEdit={hasPermission('update')}
          />
        )}

        {activeTab === 'analytics' && hasPermission('analytics') && (
          <AnalyticsDashboard />
        )}

        {activeTab === 'history' && (
          <HistoryLog />
        )}

        {activeTab === 'settings' && hasPermission('settings') && (
          <SettingsPanel />
        )}
      </main>

      {/* Модальное окно доступно только если есть права на создание/редактирование */}
      {hasPermission('create') && (
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