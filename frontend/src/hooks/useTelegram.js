useEffect(() => {
    const tg = window.Telegram?.WebApp;
    
    if (tg) {
      tg.ready();
      tg.expand();
      
      // Безопасная установка цветов
      try {
        if (tg.setHeaderColor) {
          tg.setHeaderColor('#1e40af');
        }
        if (tg.setBackgroundColor) {
          tg.setBackgroundColor('#f3f4f6');
        }
      } catch (e) {
        console.warn('Failed to set Telegram colors:', e);
      }
      
      setWebApp(tg);
      setUser(tg.initDataUnsafe?.user);
    } else {
      // Development mode
      console.warn('Telegram WebApp not found, using development mode');
      setWebApp({});
      setUser({
        id: 123456789,
        first_name: 'Test',
        last_name: 'User',
        username: 'testuser'
      });
    }
}, []);