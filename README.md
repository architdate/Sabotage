# Sabotage
An among us monitoring bot that will automatically mute players during tasks and unmute them during discussions and lobby
This project uses `amonguscapture` (the [python rewrite](https://github.com/hp3721/amonguscapture)) as a submodule for identifying the player through game memory.

## Setup
- This bot needs to run on a Windows PC which is participating in the among us game.
- The bot has to be started while you are in the menu screen or in the lobby. (It cannot be started mid-game)
- This bot needs Python 3.6+ to run. Please install it [here](https://www.python.org/downloads/)
- Install the necessary libraries using the following command
```
$ pip install -r requirements.txt
```
- Create a role for your among us players. 
- Create a voice channel in the server with permissions for `@everyone` role to NOT speak and make sure the among us players role can speak in that VC
- Follow this guide to create a discord bot and get the bot token and invite the bot: https://discordpy.readthedocs.io/en/latest/discord.html
- Make sure you give these permissions to the bot in the OAuth scope while using the guide above:
![Scope](https://i.imgur.com/liZq6tG.png)
- Rename `config.json.sample` to `config.json` and fill up all the fields.

## Usage
To use the bot:
- First all players need to register their ingame name that they use. They can re-register if the name changes too, but this needs to be done only once and not for every game
- Register ingame names using the command `/register <ingamename>`
- If you want the bot to start monitoring your game, use the `/monitor` command (once the person running the bot has started their game). If you don't do this, the bot wont interfere with your mute state
- You can tell the bot to stop monitoring using the `/stopmonitor` command
- The person running the bot can also use `/hook` to ensure that the game is hooked

## Features:
- During tasks, all players are server muted
- During lobby and menu, all players are server unmuted
- During meeting discussions, only the players who are alive are unmuted

## Contributing
To contribute to the repository, you can submit a pull request to the repository. Try to follow a format similar to the current codebase. All contributions are greatly appreciated!

## Credits:
- [@denverquane](https://github.com/denverquane) for writing the original amonguscapture repository to read game state from process ram
- [@hp3721](https://github.com/hp3721) for porting the original amonguscapture repository over to python.