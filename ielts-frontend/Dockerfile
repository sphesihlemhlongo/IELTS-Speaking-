FROM node:18-alpine AS build

# Set the working directory
WORKDIR /app

# Copy package.json and package-lock.json
COPY ./package.json ./package-lock.json ./


# Install dependencies
RUN npm install

# Copy the rest of the application
COPY . .

# Build the React app for production
RUN npm run build

# Use Nginx to serve the built React app
FROM nginx:alpine

# Copy the React build files from the previous stage
COPY --from=build /app/build /usr/share/nginx/html

# Expose port 80 for the frontend
EXPOSE 80

# Start Nginx to serve the React app
CMD ["nginx", "-g", "daemon off;"]
