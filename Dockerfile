FROM debian:bullseye-slim

WORKDIR /usr/local/lib/mlface/
RUN apt update && apt -y upgrade 
RUN apt install -y build-essential libssl-dev python3-dev python3 python3-pip python3-venv 

COPY requirements.txt requirements.txt

RUN pip3 install -r ./requirements.txt

COPY mlface.py /usr/local/lib/mlface/
COPY docker-osx.sh /usr/local/lib/mlface/
COPY lib/Algo.py /usr/local/lib/mlface/lib/
COPY known_faces/* /usr/local/lib/mlface/known_faces/

CMD ["/usr/local/lib/mlface/docker-osx.sh"]
