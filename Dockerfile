FROM python:3.8-slim
RUN mkdir /app22
WORKDIR /app22
COPY . .
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt
EXPOSE 5000
ENTRYPOINT ["python"]
CMD ["app.py"]