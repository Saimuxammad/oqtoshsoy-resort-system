FROM node:18-alpine

WORKDIR /app

# Копируем package files
COPY package*.json ./

# Устанавливаем зависимости
RUN npm install

# Копируем остальные файлы
COPY . .

# Собираем проект
RUN npm run build

# Устанавливаем serve для production
RUN npm install -g serve

# Указываем порт по умолчанию
ENV PORT=3000

# Expose port
EXPOSE 3000

# Запускаем приложение с портом по умолчанию
CMD serve -s dist -l ${PORT:-3000}