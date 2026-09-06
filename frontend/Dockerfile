# syntax=docker/dockerfile:1.7

# ---------- Build stage ----------
FROM node:20-alpine AS build

WORKDIR /app

# Install deps using the lockfile for reproducible builds.
COPY package.json package-lock.json* ./
RUN --mount=type=cache,target=/root/.npm \
    if [ -f package-lock.json ]; then npm ci; else npm install; fi

# Build the SPA.
COPY tsconfig.json vite.config.ts index.html ./
COPY src ./src
COPY public ./public

# In production the frontend calls the backend through the same origin
# (nginx /api → backend, or Kubernetes Ingress /api → backend Service), so a
# relative base URL is correct.
ENV VITE_API_BASE_URL=/api
RUN npm run build

# ---------- Runtime stage ----------
# 1.27-alpine's Alpine base had accumulated 34 CRITICAL/HIGH OS-package CVEs
# (openssl, c-ares, etc.) by CI-scan time; 1.31-alpine tracks current Alpine
# stable and drops that to 7, all in util-linux/libuuid (see .trivyignore
# at repo root for why those are accepted here).
FROM nginx:1.31-alpine AS runtime

# Non-privileged port so we can run as a non-root user.
COPY nginx.conf /etc/nginx/nginx.conf
COPY --from=build /app/dist /usr/share/nginx/html

# Prepare writable dirs for the "nginx" user (which already exists in the base image).
RUN mkdir -p /tmp/client_body /tmp/proxy /tmp/fastcgi /tmp/uwsgi /tmp/scgi \
    && chown -R nginx:nginx /tmp /usr/share/nginx/html /var/cache/nginx

USER nginx

EXPOSE 8080

STOPSIGNAL SIGQUIT

CMD ["nginx", "-g", "daemon off;"]
