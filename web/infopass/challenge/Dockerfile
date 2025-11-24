FROM python:3.13.7-slim-trixie

WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt
CMD ["flask", "run", "--host=0.0.0.0", "--port=1337"]