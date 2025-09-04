import React, { useState, useEffect } from 'react';
import { QueryClient, QueryClientProvider } from 'react-query';
import { Toaster } from 'react-hot-toast';
import toast from 'react-hot-toast';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function AppContent() {
  const [isLoading, setIsLoading] = useState(true);
  const [currentUser, setCurrentUser] = useState(null);

  useEffect(() => {
    // Простая инициализация для теста
    setTimeout(() => {
      const mockUser = {
        id: 1,
        telegram_id: 5488749868,
        first_name: 'Admin',
        last_name: 'Test',
        is_admin: true,
        can_modify: true
      };

      setCurrentUser(mockUser);
      setIsLoading(false);
      toast.success('Test rejimida ishlamoqda');
    }, 1000);
  }, []);

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
      <header className="bg-blue-600 text-white p-4">
        <div className="container mx-auto">
          <h1 className="text-2xl font-bold">Oqtoshsoy Resort System</h1>
          <p className="text-sm">Test rejimi - {currentUser?.first_name}</p>
        </div>
      </header>

      <main className="container mx-auto p-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">System ishlayapti!</h2>

          <div className="space-y-2">
            <p>✅ Frontend yuklandi</p>
            <p>✅ React ishlayapti</p>
            <p>✅ Foydalanuvchi: {currentUser?.first_name} {currentUser?.last_name}</p>
            <p>✅ Admin huquqi: {currentUser?.is_admin ? 'Ha' : 'Yo\'q'}</p>
          </div>

          <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded">
            <p className="text-sm">
              Agar bu ko'rinsa, demak asosiy muammo komponentlarda.
              Endi komponentlarni birin-ketin qo'shib test qiling.
            </p>
          </div>

          <button
            onClick={() => window.location.reload()}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Sahifani yangilash
          </button>
        </div>
      </main>
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