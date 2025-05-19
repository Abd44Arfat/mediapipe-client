FROM python:3.12

RUN apt-get update && apt-get install -y python3-distutils

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
