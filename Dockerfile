FROM python:3.8.15
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
ENTRYPOINT ["python"]
CMD ["app.py"]