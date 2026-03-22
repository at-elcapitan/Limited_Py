FROM ghcr.io/lavalink-devs/lavalink:4

USER root

WORKDIR /opt/Lavalink

COPY plugin_updater.py /opt/Lavalink/plugin_updater.py
COPY requirements.txt /opt/Lavalink/requirements.txt
COPY start.sh /opt/Lavalink/start.sh

RUN apt-get update
RUN apt-get install -y python3 python3-pip curl
RUN pip3 install --no-cache-dir -r requirements.txt
RUN chmod +x /opt/Lavalink/start.sh

ENTRYPOINT ["/opt/Lavalink/start.sh"]