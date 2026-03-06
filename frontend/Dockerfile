# Stage 1: Build Flutter web app
FROM ghcr.io/cirruslabs/flutter:stable AS build

WORKDIR /app

# Copy pubspec first for dependency caching
COPY frontend/pubspec.yaml frontend/pubspec.lock* ./
RUN flutter pub get

# Copy source and assets
COPY frontend/lib/ lib/
COPY frontend/web/ web/
COPY frontend/assets/static/ assets/static/

# Copy shared_data as assets/data (replaces symlink)
COPY shared_data/ assets/data/

# Create a minimal .env (secrets are on the backend, not frontend)
RUN echo "# Production build — no frontend secrets needed" > .env

# Build with configurable backend URL
ARG BACKEND_URL=http://localhost:8000
RUN flutter build web --release --dart-define=BACKEND_URL=$BACKEND_URL

# Stage 2: Serve with nginx
FROM nginx:alpine

COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/build/web /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
