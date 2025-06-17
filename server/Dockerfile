# server/Dockerfile

##### STAGE 1: build #####
FROM node:20-alpine AS builder
WORKDIR /app

# copy only lockfiles and package.json so install is deterministic
COPY package.json package-lock.json tsconfig.json ./

# install dev+prod deps and compile
RUN npm install
COPY src/ ./src
RUN npm run build              # produces dist/

##### STAGE 2: runtime #####
FROM node:20-alpine
WORKDIR /app

# copy compiled output and package.json
COPY --from=builder /app/dist ./dist
COPY package.json ./

# production environment
ENV NODE_ENV=production

# install only prod deps
RUN npm install --omit=dev

# Cloud Run sets $PORT for you; listen on that
CMD ["node", "dist/bootstrap.js"]
