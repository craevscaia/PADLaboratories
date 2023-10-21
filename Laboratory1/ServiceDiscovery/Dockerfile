FROM python:3.11

WORKDIR /app

EXPOSE 6000

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .
CMD ["python", "service-discovery.py"]