# books-agent frontend — React + Vite dev server.
# Kept as the Vite dev server (with proxy) to mirror the local workflow; the
# proxy target is configurable via BACKEND_URL so it can reach the backend
# container by service name.
FROM node:20-bookworm-slim

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install

COPY . .

EXPOSE 5173

# --host binds 0.0.0.0 so the dev server is reachable from outside the container.
CMD ["npm", "run", "dev", "--", "--host"]
