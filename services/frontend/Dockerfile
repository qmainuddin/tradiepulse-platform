FROM node:22-alpine AS build
WORKDIR /app

COPY package.json ./
COPY packages/contracts/package.json ./packages/contracts/
COPY apps/shell/package.json ./apps/shell/

RUN npm install

COPY packages/contracts/ ./packages/contracts/
COPY apps/shell/ ./apps/shell/

RUN npm --prefix packages/contracts run build
RUN npm --prefix apps/shell run build

FROM node:22-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production

COPY --from=build /app/package.json ./
COPY --from=build /app/apps/shell/package.json ./apps/shell/
COPY --from=build /app/packages/contracts/package.json ./packages/contracts/
COPY --from=build /app/node_modules ./node_modules
COPY --from=build /app/apps/shell/.next ./apps/shell/.next
COPY --from=build /app/apps/shell/public ./apps/shell/public

EXPOSE 3000
CMD ["npm", "--prefix", "apps/shell", "start"]
