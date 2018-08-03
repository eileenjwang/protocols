docker kill repertoire_container
docker rm repertoire_container
docker network rm repertoire-net

docker network create --driver bridge repertoire-net

docker build -t repertoire_image ..

# docker run --network audit-net -v c:/Users/p0001073/Repertoire/repo/container/data:/data -d --name repertoire_container -p 8080:8080 repertoire_image
docker run -d --network host --name repertoire_container -p 8080:8080 repertoire_image

# docker run --rm -i -t --net=host my_image telnet localhost 25
# docker exec -it repertoire_container bash
