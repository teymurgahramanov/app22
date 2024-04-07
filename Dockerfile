FROM python:3.8.15
WORKDIR /app22
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
ENTRYPOINT ["python","run.py"]