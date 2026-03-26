# Stage 1: Build
FROM node:20 as build-stage

WORKDIR /app

COPY package*.json ./
RUN npm install --legacy-peer-deps

COPY . .
RUN npm run build
RUN ls -la /app/dist

# Stage 2: Serve
FROM nginx:alpine

COPY --from=build-stage /app/dist /usr/share/nginx/html

# Expose port 80
EXPOSE 3000

CMD ["nginx", "-g", "daemon off;"]
