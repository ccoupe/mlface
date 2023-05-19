FROM ccoupe/face-recog:cuda-11.7-cudnn-8

WORKDIR /usr/local/lib/mlface/

COPY requirements.txt requirements.txt

RUN pip3 install -r ./requirements.txt

COPY mlface.py /usr/local/lib/mlface/
COPY mlface.sh /usr/local/lib/mlface/
COPY lib/Algo.py /usr/local/lib/mlface/lib/
COPY known_faces/* /usr/local/lib/mlface/known_faces/

CMD ["/usr/local/lib/mlface/mlface.sh"]
