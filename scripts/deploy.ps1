docker kill repertoire_container
docker rm repertoire_container
docker network rm repertoire-net

docker network create --driver bridge repertoire-net

docker build -t repertoire_image ..

docker run --network audit-net -v c:/Users/p0001073/Repertoire/repo/container/data:/data -d --name repertoire_container -p 8080:8080 repertoire_image
# docker exec -it repertoire_container bash
