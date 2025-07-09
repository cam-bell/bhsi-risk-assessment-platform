# Stage 1: Build the Vite app
FROM node:18-alpine AS builder

# Create and set working directory
RUN mkdir -p /app
WORKDIR /app

# Copy package files
COPY package.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application
COPY . .

# Verify src directory exists
RUN ls -la src || (echo "src directory not found" && exit 1)

# Build the Vite app
RUN npm run build

# Stage 2: Serve the static files
FROM nginx:alpine

# Create nginx directory if it doesn't exist
RUN mkdir -p /usr/share/nginx/html

# Copy the static files from the builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose the port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"] 