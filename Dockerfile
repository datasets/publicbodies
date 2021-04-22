# DESCRIPTION: publicbodies.org website
# BUILD: docker build --rm -t publicbodies .
# 
# If you want to just build the documentation portal locally, do:
#   docker build --rm -t publicbodies .
# to build the container, then run
#   docker run --rm --volume="$PWD:/home/node/portal" -it publicbodies node index.js
# open http://localhost:3000 on your browser to see the portal.

FROM node:12

# Never prompt the user for choices on installation/configuration of packages
ENV DEBIAN_FRONTEND noninteractive
ENV TERM linux
ENV NODE_ENV=production
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

# port Docusaurus runs on
EXPOSE 3000
