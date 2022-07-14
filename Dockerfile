FROM python:3.10.2
RUN mkdir /test22
WORKDIR /test22
COPY test22.py test22.yaml requirements.txt ./
RUN python -m pip install --upgrade pip
RUN python -m pip install -r requirements.txt
ENTRYPOINT ["python"]
CMD ["-u","test22.py"]