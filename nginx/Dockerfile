# Build context is the REPO ROOT (see docker-compose "nginx" service):
#   docker build -f nginx/Dockerfile .
# Stage 1 builds the Vue SPA; stage 2 serves it via Nginx + proxies /api.
FROM node:18-alpine AS frontend-build

WORKDIR /build
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
# Same-origin API access: empty VITE_API_URL makes api.js use relative
# URLs, which Nginx proxies to FastAPI.
ENV VITE_API_URL=""
RUN npm run build

FROM nginx:alpine

COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=frontend-build /build/dist /usr/share/nginx/html

EXPOSE 80
