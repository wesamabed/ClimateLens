# server/Dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json tsconfig*.json ./
RUN npm install
COPY src/ ./src
RUN npm run build          # outputs to dist/

FROM node:20-alpine AS runtime
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY package*.json ./
ENV NODE_ENV=production
RUN npm ci --omit=dev
CMD ["node", "dist/bootstrap.js"]
