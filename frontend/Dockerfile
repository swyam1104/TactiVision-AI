FROM node:18-alpine

WORKDIR /app

# Copy package configurations
COPY package.json ./

# Install packages
RUN npm install

# Copy application source
COPY . .

# Expose port
EXPOSE 3000

# Next.js dev server command
CMD ["npm", "run", "dev"]
