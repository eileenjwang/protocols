docker kill protocols_container
docker rm protocols_container

docker build -t protocols_image ..
docker run -d --name protocols_container -p 8008:8008 protocols_image
# docker exec -it protocols_container bash