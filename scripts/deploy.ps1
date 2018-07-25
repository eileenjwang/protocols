docker kill protocols_container
docker rm protocols_container

docker build -t protocols_image ..

docker run  -v c:/Users/p0001073/Protocoles/repo/container/data:/data -d --name protocols_container -p 8008:8008 protocols_image
# docker exec -it protocols_container bash
