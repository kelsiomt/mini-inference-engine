FROM python:3.11-slim

WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*
RUN pip install --upgrade pip

COPY requirements.txt /app
RUN cd /app
RUN pip install -r requirements.txt
RUN python -m spacy download pt_core_news_sm

COPY . /app

EXPOSE 8080

CMD ["python", "app.py"]