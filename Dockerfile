# 1) deps stage: install all workspaces for build
FROM node:20-alpine AS deps
WORKDIR /app

# copy root manifests + server manifest
COPY package.json package-lock.json ./
COPY server/package.json ./server/

# install everything so we can build server
RUN npm ci

# 2) builder stage: compile the server
FROM deps AS builder
WORKDIR /app

# bring in server source
COPY server ./server

# build just the server workspace
RUN npm run build --workspace=server

# 3) runtime stage: install only server’s prod deps + copy in dist
FROM node:20-alpine AS runtime
WORKDIR /app

# use server's package.json as the sole manifest
COPY server/package.json ./package.json
# still use your root lockfile to lock versions
COPY package-lock.json ./

# install only production dependencies
RUN npm ci --omit=dev

# copy over the compiled server code
COPY --from=builder /app/server/dist ./dist

# runtime config
ENV NODE_ENV=production PORT=3000
EXPOSE 3000

# launch
CMD ["node", "dist/bootstrap.js"]
