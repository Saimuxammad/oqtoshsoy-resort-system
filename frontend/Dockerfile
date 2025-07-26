FROM node:18-alpine

WORKDIR /app

# Копируем package files
COPY package*.json ./

# Устанавливаем зависимости включая terser
RUN npm install
RUN npm install --save-dev terser

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