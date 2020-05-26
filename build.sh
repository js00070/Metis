cd uweb && npm run build && cd ..

docker build -t js00070/metis-web . -f docker/metis-web.dockerfile

docker build -t js00070/metis-svr . -f docker/metis-svr.dockerfile