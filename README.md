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
DISCORD_TOKEN =       # Your bot token
PASSWD =              # Lavalink server password
DBHOST =              # URL to your PostgreSQL DB
DBUSER =              # Your PostgreSQL DB username
DBPASS =              # PostgreSQL DB password
SPCLNT =              # Spotify client key
SPSECR =              # Spotify secret
```


### Setting up PostgreSQL database

Create a database named `nextmdb` and then table using the following query:

```sql
create table if not exists music_data (
	id serial primary key,
	music_name text not null,
	music_url text not null,
	user_id bigint not null
);
```

With the configuration in place, your bot is now ready to use. Simply run the `run.sh` or `run.bat` file to start it.


## Commands

| Command Name      | Description                                        |
| ----------------- | -------------------------------------------------- |
| sc.inspect        | Displays all command list                          |
| /youtube          | Play a YouTube track                               |
| /soundcloud       | Play a SoundCloud track                            |
| /spotify          | Play a Spotify track                               |
| /resend_control   | Resend the music control panel                     |
| /seek             | Seek the current soundtrack                        |
| /clear            | Delete a song from the queue                       |
| /list display     | Display the user list                              |
| /list remove      | Remove a song from the user list                   |
| /list add         | Add a song to the user list                        |
| /list play        | Play songs from the user list                      |
| /jmp              | Changes song to position                           |
