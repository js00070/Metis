# FROM node:10-stretch

# ADD uweb /metis/uweb
# WORKDIR /metis/uweb

# RUN npm install

# ENTRYPOINT ["npm","run","start"]

FROM nginx

COPY uweb/nginx.conf /etc/nginx/conf.d/default.conf

ADD uweb/dist /usr/share/nginx/html

CMD nginx -g "daemon off;"