# Build stage
FROM node:18-alpine as builder

WORKDIR /app

# Копируем package files
COPY package*.json ./
RUN npm ci

# Копируем исходники и собираем
COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine

# Копируем собранные файлы
COPY --from=builder /app/dist /usr/share/nginx/html

# Копируем конфигурацию nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]