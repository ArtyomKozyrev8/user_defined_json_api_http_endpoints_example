FROM python:3.9.9-alpine

WORKDIR /usr/src

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD python3 -m aiohttp.web -H 0.0.0.0 -P 5879 http_server_app:init_func_standalone