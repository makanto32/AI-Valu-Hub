FROM mcr.microsoft.com/devcontainers/javascript-node:20-bullseye AS build

WORKDIR /app

ARG VITE_API_URL=https://aihub-api-dev.yellowwave-f693504a.eastus.azurecontainerapps.io
ENV VITE_API_URL=${VITE_API_URL}

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM mcr.microsoft.com/devcontainers/base:ubuntu AS runtime

RUN apt-get update \
	&& DEBIAN_FRONTEND=noninteractive apt-get install -y nginx \
	&& rm -rf /var/lib/apt/lists/*

COPY nginx.conf /etc/nginx/sites-available/default
COPY --from=build /app/dist /var/www/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]