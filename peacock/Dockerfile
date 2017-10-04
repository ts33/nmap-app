# Use an official node runtime as a parent image
FROM node:8.6.0-alpine

# Create app directory
WORKDIR /usr/src/app

# Install app dependencies
COPY package.json package-lock.json ./

# install dependencies
RUN npm install

# Bundle app source
COPY . .

# export port
EXPOSE 3001

# start app
CMD [ "npm", "start" ]
