FROM node:20-alpine

WORKDIR /app

COPY package.json ./
RUN npm install

COPY . .

ENV NITRO_HOST=0.0.0.0
ENV NITRO_PORT=3000

EXPOSE 3000

CMD ["npm", "run", "dev"]
