FROM oven/bun:1 AS dependencies-env
COPY ./package.json ./bun.lock /app/
WORKDIR /app
RUN bun install

FROM node:20-alpine AS build-env
COPY --from=dependencies-env /app/node_modules /app/node_modules
COPY . /app/
WORKDIR /app
# Utiliser Node.js pour le build au lieu de Bun
RUN npm run build



FROM nginx:alpine
LABEL org.opencontainers.image.authors="Cesar Richard <cesar@crichard.fr>"
LABEL org.opencontainers.image.source="https://github.com/cesar-richard-ei/france-tocarde"

# Créer les répertoires nécessaires avec les bonnes permissions
RUN mkdir -p /var/cache/nginx/client_temp \
    /var/cache/nginx/proxy_temp \
    /var/cache/nginx/fastcgi_temp \
    /var/cache/nginx/uwsgi_temp \
    /var/cache/nginx/scgi_temp \
    /tmp/client_body \
    /tmp/proxy_temp \
    /tmp/fastcgi_temp \
    /tmp/uwsgi_temp \
    /tmp/scgi_temp \
    /run/nginx && \
    chmod -R 777 /var/cache/nginx /tmp /run/nginx && \
    touch /run/nginx/nginx.pid && \
    chmod 777 /run/nginx/nginx.pid

# Copier la config Nginx principale avec le chemin du pid personnalisé
COPY nginx/nginx-main.conf /etc/nginx/nginx.conf

# Copier la config Nginx spécifique au serveur
COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf

# Copier les fichiers statiques du frontend
COPY --from=build-env /app/build/client/ /usr/share/nginx/html

# Exposer le port 80
EXPOSE 80

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
CMD wget --no-verbose --tries=1 --spider http://localhost:80/ || exit 1
