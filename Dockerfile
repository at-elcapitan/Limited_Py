FROM python:3.10-alpine

WORKDIR /opt/nxre

COPY requirements.txt requirements.txt
COPY atlb/ atlb/

RUN apk add --no-cache gcc musl-dev linux-headers postgresql libpq-dev
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "atlb"]