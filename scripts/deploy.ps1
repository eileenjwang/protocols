docker kill protocols_container
docker rm protocols_container
docker network rm protocols-net

docker network create --driver bridge protocols-net

docker build -t protocols_image ..

docker run --network audit-net -v c:/Users/p0001073/Repertoire/repo/container/data:/data -d --name protocols_container -p 8080:8080 protocols_image
# docker exec -it protocols_container bash
