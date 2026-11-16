FROM a7p5-api:acceptance
# Reuse the already exported Debian/JRE base and the exact verified Node
# binary, avoiding a second registry dependency during customer installation.
ENTRYPOINT []
COPY node /usr/local/bin/node
COPY node-LICENSE /usr/local/share/licenses/node-LICENSE
WORKDIR /web
COPY package.json pnpm-workspace.yaml ./
COPY node_modules ./node_modules
COPY apps/web ./apps/web
WORKDIR /web/apps/web
ENV HOST=127.0.0.1 PORT=15173 NODE_ENV=production
CMD ["node", "node_modules/@react-router/serve/bin.js", "./build/server/index.js"]
