FROM python:3.10-alpine
WORKDIR /docker_nextbot
RUN apk add --no-cache gcc musl-dev linux-headers postgresql libpq-dev
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY atlb/ atlb/
ENV TZ=Europe/Kyiv
COPY . .
CMD ["python", "atlb"]