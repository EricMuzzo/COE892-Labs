FROM python:3.13.2-slim

WORKDIR /api

COPY ./requirements.txt /api/requirements.txt

RUN pip install --upgrade pip==25.0.1
RUN pip install --no-cache-dir -r /api/requirements.txt

COPY ./app /api/app

CMD ["fastapi", "run", "app/main.py", "--port", "80"]