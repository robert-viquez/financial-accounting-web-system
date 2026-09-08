FROM node:24-alpine AS build

WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
ARG VITE_API_URL=/api/
ARG VITE_DEMO_MODE=false
ARG VITE_DEMO_USERNAME=
ARG VITE_DEMO_PASSWORD=
ENV VITE_API_URL=$VITE_API_URL
ENV VITE_DEMO_MODE=$VITE_DEMO_MODE
ENV VITE_DEMO_USERNAME=$VITE_DEMO_USERNAME
ENV VITE_DEMO_PASSWORD=$VITE_DEMO_PASSWORD
RUN npm run build

FROM nginx:1.29-alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
