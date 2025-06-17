# server/Dockerfile
FROM node:20-alpine

# 1) Install globally the TypeScript‐runtime tool we need
RUN npm install -g ts-node ts-node-dev typescript

WORKDIR /app

# 2) Copy lockfile & package.json so install is reproducible
COPY package*.json ./

# 3) Install everything (including devDependencies)
RUN npm ci

# 4) Copy the rest of your source
COPY src/ ./src

# 5) Ensure .env is not left behind in the image
#    (we'll pass variables in via Cloud Run config)
RUN rm -f .env

# 6) Expose your port
EXPOSE 3000

# 7) Start the server via ts-node-dev
#    (matches your local `npm run dev` command)
CMD ["ts-node-dev", "--respawn", "--transpile-only", "src/bootstrap.ts"]
