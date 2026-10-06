# docker file for flask app
FROM python:3.11-slim

WORKDIR /app

# install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy everything else
COPY . .

# expose flask port
EXPOSE 5000

ENV FLASK_APP=app.py

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
