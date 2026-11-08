# Production image for the SvelteKit app (adapter-node), deployed by Coolify as the `client` app.
# Build with: docker build --build-arg PUBLIC_GRAPHQL_ENDPOINT=https://<api host>/graphql/ web/

# Keep the major version in step with .node-version.
FROM node:26-slim AS build
WORKDIR /app

# Node 25+ no longer ships corepack, so install the pnpm that package.json's packageManager names.
RUN npm install -g pnpm@10.32.1

COPY package.json pnpm-lock.yaml pnpm-workspace.yaml .npmrc ./
RUN pnpm install --frozen-lockfile

COPY . .

# Houdini bakes the API URL into the generated client at build time (see houdini.config.js),
# so it is a build argument; Coolify passes it when the variable is marked as a build variable.
ARG PUBLIC_GRAPHQL_ENDPOINT
RUN test -n "$PUBLIC_GRAPHQL_ENDPOINT" || { echo "PUBLIC_GRAPHQL_ENDPOINT build arg is required" >&2; exit 1; }
ENV PUBLIC_GRAPHQL_ENDPOINT=$PUBLIC_GRAPHQL_ENDPOINT
RUN pnpm run build

FROM node:26-slim
WORKDIR /app
ENV NODE_ENV=production PORT=3000
COPY --from=build /app/package.json ./
COPY --from=build /app/build ./build
USER node
EXPOSE 3000
CMD ["node", "build/index.js"]
