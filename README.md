# Limited nEXT Bot

Limited nEXT is a music bot for Discord, part of the 'Limited' bot family. It is written in Python and utilizes the Discord.py 2.0 library along with the Wavelink library for music functionality.

## About

Limited nEXT is one of the bots in the 'Limited' series, which includes:

- [Limited nEXT](https://github.com/at-elcapitan/Limited_Py) (this bot)
- [Limited C/Link](https://github.com/at-elcapitan/Limited-C_Link)
- [Limited jEXT](https://github.com/at-elcapitan/AT-Limited_jEXT)

The bot is designed to provide a seamless music streaming experience on Discord, and it is equipped with features that make it stand out.


## Bot Setup and Usage

To get started with Limited nEXT, follow these steps:

Clone this repository to your local machine using the Git program:

```sh
 git clone https://github.com/at-elcapitan/Limited_Py.git
```


### Configuring

Create a `docker.env` file in the bot's directory and fill it with your specific values. The file should follow this pattern:

```yaml
DISCORD_TOKEN = your_token
PASSWD = youshallnotpass
LVHOST = lavalink:2333
DBHOST = postgres
DBUSER = postgres
DBPASS = yourpassword
```

Don't forget to replace `DISCORD_TOKEN` with your value. 

With the configuration in place, your bot is now ready to use. Simply run the `docker-compose up -d` command. Bot, Lavalink and PostgreSQL DB will be created and initialized automatically.

### Warning

If you will modify the `application.yml` or `docker-compose.yaml`, to prevent them from being overwritten, use the following commands:

```sh
git update-index --skip-worktree application.yml
```

```sh
git update-index --skip-worktree docker-compose.yaml
```

## Commands

| Command Name      | Description                                        |
| ----------------- | -------------------------------------------------- |
| sc.inspect        | Displays all command list                          |
| /youtube          | Play a YouTube track                               |
| /soundcloud       | Play a SoundCloud track                            |
| /resend_control   | Resend the music control panel                     |
| /seek             | Seek the current soundtrack                        |
| /remove           | Delete a song from the queue                       |
| /list display     | Display the user list                              |
| /list remove      | Remove a song from the user list                   |
| /list add         | Add a song to the user list                        |
| /list add_current | Adds current (playing) song from queue to list     |
| /list play        | Play songs from the user list                      |
| /jmp              | Changes song to position                           |

## Using external PostgreSQL Database

For using your own external DB, you have to edit `docker-compose.yaml`. Use this pattern:

```yaml
version: '3.8'

services:
  nEXT:
    restart: unless-stopped
    image: atproject/limitednext:lastest
    container_name: limitednext
    build:
      context: .
      dockerfile: ./Dockerfile
    network_mode: host
    depends_on:
      - lavalink
    command: python atlb
    env_file: docker.env

  lavalink:
    image: ghcr.io/lavalink-devs/lavalink:4
    container_name: lavalink
    restart: unless-stopped
    environment:
      - _JAVA_OPTIONS=-Xmx6G
      - SERVER_PORT=2333
      - LAVALINK_SERVER_PASSWORD=youshallnotpass
    volumes:
      - ./application.yml:/opt/Lavalink/application.yml
    expose:
      - 2333
    ports:
      - "2333:2333"
```

And do not forget to replace `LVHOST` variable from `docker.env` file with the real Lavalink address.
