FROM node:18-alpine

WORKDIR /app

# Копируем package files
COPY package*.json ./

# Устанавливаем зависимости включая dev dependencies
RUN npm install

# Копируем остальные файлы
COPY . .

# Собираем проект
RUN npm run build

# Устанавливаем serve для production
RUN npm install -g serve

# Expose port
EXPOSE 3000

# Запускаем приложение
CMD serve -s dist -l $PORT