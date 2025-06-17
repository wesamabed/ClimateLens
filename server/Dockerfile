# Use a slim Node.js image for smaller size
FROM node:20-alpine AS build

# Install dependencies for building
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install

# Copy source and build TypeScript
COPY src/ ./src
RUN npm run build # This will run your "tsc -p tsconfig.json" script

# --- Production Stage ---
FROM node:20-alpine

WORKDIR /app

# Copy only production dependencies and compiled code from the build stage
COPY --from=build /app/package.json /app/package-lock.json* ./
RUN npm install --omit=dev # Install only production dependencies

COPY --from=build /app/dist ./dist # Copy the compiled JavaScript

# Remove any stray .env (good practice, as env vars are set by Cloud Run)
RUN rm -f .env

# Expose the port your application listens on
EXPOSE 3000

# Start the server using the compiled JavaScript
CMD ["node", "dist/bootstrap.js"]