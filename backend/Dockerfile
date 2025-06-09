FROM python:3.12.12

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

# Download spacy models
RUN python -m spacy download en_core_web_sm
RUN python -m spacy download fr_core_news_sm

COPY . .

EXPOSE 5000

CMD ["python", "app/main.py"]
