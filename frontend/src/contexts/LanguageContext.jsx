import React, { createContext, useContext, useState, useEffect } from 'react';

const translations = {
  uz: {
    // Navigation
    rooms: 'Xonalar',
    bookings: 'Bronlar',
    calendar: 'Kalendar',
    analytics: 'Tahlil',
    history: 'Tarix',
    settings: 'Sozlamalar',

    // Common
    loading: 'Yuklanmoqda...',
    error: 'Xatolik',
    save: 'Saqlash',
    cancel: 'Bekor qilish',
    delete: 'O\'chirish',
    edit: 'Tahrirlash',
    close: 'Yopish',
    search: 'Qidirish',
    filter: 'Filtrlash',
    refresh: 'Yangilash',
    export: 'Eksport',
    noData: 'Ma\'lumot yo\'q',

    // Rooms
    roomNumber: 'Xona raqami',
    roomType: 'Xona turi',
    status: 'Holati',
    available: 'Bo\'sh',
    occupied: 'Band',
    price: 'Narxi',
    capacity: 'Sig\'imi',

    // Bookings
    createBooking: 'Bron yaratish',
    updateBooking: 'Bronni yangilash',
    deleteBooking: 'Bronni o\'chirish',
    bookingDetails: 'Bron tafsilotlari',
    guestName: 'Mehmon ismi',
    checkIn: 'Kirish sanasi',
    checkOut: 'Chiqish sanasi',
    notes: 'Izohlar',
    duration: 'Muddat',
    totalBookings: 'Jami bronlar',

    // Analytics
    occupancyStats: 'Bandlik statistikasi',
    averageOccupancy: 'O\'rtacha bandlik',
    totalRevenue: 'Umumiy daromad',
    dailyStats: 'Kunlik statistika',
    monthlyStats: 'Oylik statistika',
    roomTypeStats: 'Xona turi statistikasi',
    trends: 'Tendensiyalar',
    forecast: 'Prognoz',
    exportExcel: 'Excel eksport',

    // History
    actionHistory: 'Harakatlar tarixi',
    recentActivity: 'So\'nggi faoliyat',
    created: 'yaratildi',
    updated: 'yangilandi',
    deleted: 'o\'chirildi',
    by: 'tomonidan',
    at: 'da',

    // Settings
    language: 'Til',
    notifications: 'Bildirishnomalar',
    theme: 'Mavzu',
    lightTheme: 'Yorug\' mavzu',
    darkTheme: 'Qorong\'i mavzu',
    enableNotifications: 'Bildirishnomalarni yoqish',
    user: 'Foydalanuvchi',

    // Messages
    bookingCreated: 'Bron muvaffaqiyatli yaratildi',
    bookingUpdated: 'Bron muvaffaqiyatli yangilandi',
    bookingDeleted: 'Bron muvaffaqiyatli o\'chirildi',
    confirmDelete: 'Bronni o\'chirishni tasdiqlaysizmi?',
    networkError: 'Tarmoq xatosi',
    serverError: 'Server xatosi',
    validationError: 'Tekshiruv xatosi',
    notAuthorized: 'Ruxsat yo\'q',
  },

  ru: {
    // Navigation
    rooms: 'Xonalar',
    bookings: 'Брони',
    calendar: 'Календарь',
    analytics: 'Аналитика',
    history: 'История',
    settings: 'Настройки',

    // Common
    loading: 'Загрузка...',
    error: 'Ошибка',
    save: 'Сохранить',
    cancel: 'Отмена',
    delete: 'Удалить',
    edit: 'Редактировать',
    close: 'Закрыть',
    search: 'Поиск',
    filter: 'Фильтр',
    refresh: 'Обновить',
    export: 'Экспорт',
    noData: 'Нет данных',

    // Rooms
    roomNumber: 'Номер комнаты',
    roomType: 'Тип номера',
    status: 'Статус',
    available: 'Свободен',
    occupied: 'Занят',
    price: 'Цена',
    capacity: 'Вместимость',

    // Bookings
    createBooking: 'Создать бронь',
    updateBooking: 'Обновить бронь',
    deleteBooking: 'Удалить бронь',
    bookingDetails: 'Детали брони',
    guestName: 'Имя гостя',
    checkIn: 'Дата заезда',
    checkOut: 'Дата выезда',
    notes: 'Примечания',
    duration: 'Продолжительность',
    totalBookings: 'Всего броней',

    // Analytics
    occupancyStats: 'Статистика занятости',
    averageOccupancy: 'Средняя занятость',
    totalRevenue: 'Общий доход',
    dailyStats: 'Дневная статистика',
    monthlyStats: 'Месячная статистика',
    roomTypeStats: 'Статистика по типам',
    trends: 'Тренды',
    forecast: 'Прогноз',
    exportExcel: 'Экспорт в Excel',

    // History
    actionHistory: 'История действий',
    recentActivity: 'Последняя активность',
    created: 'создан',
    updated: 'обновлен',
    deleted: 'удален',
    by: 'пользователем',
    at: 'в',

    // Settings
    language: 'Язык',
    notifications: 'Уведомления',
    theme: 'Тема',
    lightTheme: 'Светлая тема',
    darkTheme: 'Темная тема',
    enableNotifications: 'Включить уведомления',
    user: 'Пользователь',

    // Messages
    bookingCreated: 'Бронь успешно создана',
    bookingUpdated: 'Бронь успешно обновлена',
    bookingDeleted: 'Бронь успешно удалена',
    confirmDelete: 'Подтвердите удаление брони?',
    networkError: 'Ошибка сети',
    serverError: 'Ошибка сервера',
    validationError: 'Ошибка валидации',
    notAuthorized: 'Нет доступа',
  }
};

const LanguageContext = createContext();

export function LanguageProvider({ children }) {
  const [language, setLanguage] = useState(() => {
    // Получаем сохраненный язык или язык из Telegram
    const saved = localStorage.getItem('language');
    const telegramLang = window.Telegram?.WebApp?.initDataUnsafe?.user?.language_code;

    if (saved) return saved;
    if (telegramLang === 'ru') return 'ru';
    return 'uz';
  });

  useEffect(() => {
    localStorage.setItem('language', language);
  }, [language]);

  const t = (key) => {
    return translations[language][key] || key;
  };

  const changeLanguage = (lang) => {
    if (translations[lang]) {
      setLanguage(lang);
    }
  };

  return (
    <LanguageContext.Provider value={{ language, t, changeLanguage }}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
}