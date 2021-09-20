# DESCRIPTION: publicbodies.org website
# BUILD: docker build --rm -t publicbodies .
# 
# If you want to build the portal locally in development mode, do:
#   docker build --rm -t publicbodies . --build-arg NODE_ENV=development
# to build the container, then run
#   docker run --rm --name publicbodies -p 3000:3000 -it publicbodies node index.js
# open http://localhost:3000 on your browser to see the portal.

FROM node:12

ARG NODE_ENV=production

# Never prompt the user for choices on installation/configuration of packages
ENV DEBIAN_FRONTEND noninteractive
ENV TERM linux
ENV NODE_ENV=$NODE_ENV
# from https://github.com/nodejs/docker-node/blob/main/docs/BestPractices.md#global-npm-dependencies
ENV NPM_CONFIG_PREFIX=/home/node/.npm-global
ENV PATH=$PATH:/home/node/.npm-global/bin

# use non-priviledged user provided by node's docker image
USER node

# install dependencies
RUN mkdir -p /home/node/portal
COPY ./package.json /home/node/portal/package.json
WORKDIR /home/node/portal
RUN npm install .

# copy website resources
COPY ./lib /home/node/portal/lib
COPY ./routes /home/node/portal/routes
COPY ./views /home/node/portal/views
COPY ./public /home/node/portal/public
COPY ./data /home/node/portal/data
COPY ./index.js /home/node/portal/

# port Docusaurus runs on
EXPOSE 3000
