FROM python:3.13.7-slim-trixie

WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt
CMD ["hypercorn", "server:app", "--bind=0.0.0.0:9999"]