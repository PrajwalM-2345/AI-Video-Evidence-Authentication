# Use Node 22 to satisfy Vite's requirements
FROM node:22-alpine

WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Using a simple serve to host the static build
RUN npm install -g serve
CMD ["serve", "-s", "dist", "-l", "5173"]