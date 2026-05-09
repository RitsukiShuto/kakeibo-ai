# 1. Build stage
FROM node:20-slim AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# 2. Production stage
FROM nginx:stable-alpine
COPY --from=builder /app/dist /usr/share/nginx/html
# Nginx configuration will be mounted or copied
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
