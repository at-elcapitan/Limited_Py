# nEXT Reemerged (nXRE)

Limited nEXT is a music bot for Discord, part of the 'Limited' bot family. It is written in Python and utilizes the Discord.py 2.0 library along with the Mafic library for music functionality.

## About

The bot is designed to provide a seamless music streaming experience on Discord, and it is equipped with features that make it stand out.


## Bot Setup and Usage

To get started with Limited nEXT, follow these steps:

Clone this repository to your local machine using the Git program:

```sh
 git clone https://github.com/at-elcapitan/Limited_Py.git
```

### Configuring

Create a `.env` file in the bot's directory and fill it with your specific values. The file should follow this pattern:

```yaml
DISCORD_TOKEN=your_token
PASSWD=youshallnotpass
LVHOST=lavalink:2333
DBHOST=postgres
DBUSER=postgres
DBPASS=yourpassword
LOGLEVEL=INFO
```

> [!NOTE]
> LOGLEVEL is an optional environment variable. You can remove it and loglevel will be set to INFO

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
| /resend_control   | Resend the music control panel                     |
| /seek             | Seek the current soundtrack                        |
| /remove           | Delete a song from the queue                       |
| /jmp              | Changes song to position                           |
