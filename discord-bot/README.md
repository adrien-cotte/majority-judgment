# Major Bot for Discord

<img src="../img/logo.png" alt="Logo" width="100"/>

This is a Discord bot script, `major_bot.py`, designed to interact with specific guilds on 
Discord. The bot is built using the `disnake` library, a fork of `discord.py` that adds 
support for Discord's interactions API.

This bot is dedicated to https://github.com/adrien-cotte/majority-judgment project.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Configuration](#configuration)
- [Setting Up Environment Variables](#setting-up-environment-variables)
- [Running the Bot](#running-the-bot)
- [Docker](#Docker)
- [Commands Usage](#commands-usage)
- [How to create your first Discord bot](#how-to-create-your-first-discord-bot)
- [How to invite bot to your Discord server](#how-to-invite-bot-to-your-discord-server)
- [How to get MAJOR\_BOT\_TOKEN](#how-to-get-major_bot_token)
- [How to get MAJOR\_BOT\_GUILDS](#how-to-get-major_bot_guilds)

## Prerequisites

### Discord bot knowledge

If you are not familiar with a Discord bot management, then here is where you should start: https://discord.com/developers/docs/getting-started
The following sections can help you too:
- [How to create your first Discord bot](#how-to-create-your-first-discord-bot)
- [How to invite bot to your Discord server](#how-to-invite-bot-to-your-discord-server)
- [How to get MAJOR_BOT_TOKEN](#how-to-get-major_bot_token)
- [How to get MAJOR_BOT_GUILDS](#how-to-get-major_bot_guilds)

### Python modules

Before you start, ensure you have Python installed on your system and the `disnake 2.9+`
library. You can install `disnake` using pip:

```bash
pip install disnake
```

Ensure to have Majority Judgment others dependencies: [README#requirements](../README.md#requirements)

## Configuration

The bot requires two environment variables for its configuration:

1. `MAJOR_BOT_TOKEN`: The bot's token for authentication with the Discord API. See [How to get MAJOR_BOT_TOKEN](#how-to-get-major_bot_token) for more details.

2. `MAJOR_BOT_GUILDS`: A comma-separated list of Discord Guild IDs where the bot will be 
active (keep empty for any server). See [How to get MAJOR_BOT_GUILDS](#how-to-get-major_bot_guilds) for more details.

## Setting Up Environment Variables

Set the environment variables in your terminal:

For Linux/macOS:

```bash
export MAJOR_BOT_GUILDS=123456789012345678,987654321098765432,...
export MAJOR_BOT_TOKEN=<YOUR_BOT_TOKEN>
```

For Windows (using Command Prompt):

```cmd
set MAJOR_BOT_GUILDS=123456789012345678,987654321098765432,...
set MAJOR_BOT_TOKEN=<YOUR_BOT_TOKEN>
```

## Running the Bot

Navigate to the directory containing `major_bot.py` and run the script:

```bash
./major_bot.py
```

Ensure that `major_bot.py` is executable. If it's not, you can make it executable on 
Linux/macOS with `chmod +x major_bot.py`.

## Docker

You can deploy the Majority Judgement Discord bot using Docker for easier setup and consistent environments.
This section provides instructions on how to build and run the Docker container.

### Building the Docker Image

To build the Docker image, run the following command in the directory containing `discord-bot.Dockerfile`:

```bash
docker build -f discord-bot.Dockerfile \
  -e MAJOR_BOT_TOKEN='your_bot_token_here' \
  -e MAJOR_BOT_GUILDS='your_guild_ids_here' \
  -t major-bot
```

This command builds the Docker image and tags it as `major-bot`.

### Running the Docker Container

```bash
docker run -d major-bot
```

## Commands Usage

### /major_create
- **Description**: Create a new Majority Judgment (only one at a time is allowed for now)
- **Options**:
  - *question*: The Majority Judgment purpose
  - *choices*: The Majority Judgment candidates/choices, separated by a semicolon (`;`)
- **Example**: `/major_create question: The best Discord API choices: JS;Java;Python`

### /major_display
- **Description**: Display the current Majority Judgment results
- **Options**:
  - *visibility*: Display results in a public or private message
- **Example**: `/major_display visibilité:privé`

### /major_delete
- **Description**: Delete the current Majority Judgment
- **Options**: N/A
- **Example**: `/major_delete`

## How to create your first Discord bot

Go to your developper space: https://discord.com/developers/applications

And create a new app.

![alt text](img/discord-bot_new.png)
![alt text](img/discord-bot_create.png)

Then, go to on OAuth2 -> URL Generator -> bot.

![alt text](img/discord-bot_install.png)

Done, congratulations!

## How to invite bot to your Discord server

Go to your Discord developper space, select your app,
and click on OAuth2 -> URL Generator -> bot -> Administrator -> Generated URL.

![alt text](img/discord-bot_url_example.png)

Copy this url in your Discord server and click on it:

![alt text](img/discord-bot_link.png)

Continue.

![alt text](img/discord-bot_link_continue.png)

Authorize.

![alt text](img/discord-bot_authorize.png)

Now, export `MAJOR_BOT_TOKEN` and `MAJOR_BOT_GUILDS` to run `major_bot.py`.

## How to get MAJOR_BOT_TOKEN

Go to https://discord.com/developers/applications, then Bot -> Token.

![alt text](img/discord-bot_token_example.png)

## How to get MAJOR_BOT_GUILDS

Got to your Discord app.
Then, be sure the Developer mode is activated.

![alt text](img/discord-bot_dev_example.png)

Right-click of your server icon and select `Copy Server ID`.

![alt text](img/discord-bot_guild_id_example.png)
