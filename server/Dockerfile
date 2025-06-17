# server/Dockerfile

FROM node:20-alpine

# install ts-runtime tools
RUN npm install -g ts-node ts-node-dev typescript

WORKDIR /app

# copy only the two files that drive install
COPY package.json package-lock.json* ./

# install *everything* (dev + prod) so your tests & ts-node-dev still work
RUN npm install

# bring in your source
COPY src/ ./src

# remove any stray .env
RUN rm -f .env

# expose your port
EXPOSE 3000

# start the server with your existing ts-node-dev bootstrap command
CMD ["ts-node-dev", "--respawn", "--transpile-only", "src/bootstrap.ts"]
