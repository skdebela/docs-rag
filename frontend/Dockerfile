# Build stage
FROM node:20 AS build
WORKDIR /frontend
COPY . /frontend/
RUN npm install && npm run build

# Serve stage
FROM node:20-slim AS serve
WORKDIR /frontend
COPY --from=build /frontend/dist /frontend/dist
RUN npm install -g serve
EXPOSE 5173
CMD ["serve", "-s", "dist", "-l", "5173"]
