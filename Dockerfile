FROM python:3.8.5
RUN mkdir /app
WORKDIR /app
COPY . .
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt
EXPOSE 5000
ENTRYPOINT ["python"]
CMD ["app.py"]