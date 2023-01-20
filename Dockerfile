FROM ccoupe:dlib

WORKDIR /usr/local/lib/mlface/

COPY requirements.txt requirements.txt

RUN pip3 install -r ./requirements.txt

COPY mlface.py /usr/local/lib/mlface/
COPY docker-mlface.sh /usr/local/lib/mlface/
COPY lib/Algo.py /usr/local/lib/mlface/lib/

CMD ["/usr/local/lib/mlface/docker-mlface.sh"]

