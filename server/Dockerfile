# server/Dockerfile

#### 1. build stage ####
FROM node:20-alpine AS builder
WORKDIR /app

# only copy lockfile + manifest, install ALL deps for build/test
COPY package.json package-lock.json ./
RUN npm ci

# copy all source & compile to dist/
COPY tsconfig.json ./
COPY src ./src
RUN npm run build     # produces ./dist

#### 2. runtime stage ####
FROM node:20-alpine AS runtime
WORKDIR /app

# copy only production deps, then drop devDeps
COPY package.json package-lock.json ./
RUN npm ci --omit=dev

# copy compiled output
COPY --from=builder /app/dist ./dist

# tell Cloud Run the PORT is injected in env
ENV NODE_ENV=production

# run the compiled JS
CMD ["node", "dist/bootstrap.js"]
