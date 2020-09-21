import discord, json
from discord.ext import commands

import sys, traceback

def get_prefix(bot, message):
    """A callable Prefix for our bot. This could be edited to allow per server prefixes."""
    prefixes = ['/']
    return commands.when_mentioned_or(*prefixes)(bot, message)


initial_extensions = ['cogs.gamehandler',
                      'cogs.owner']

bot = commands.Bot(command_prefix=get_prefix, description='Among Us dicord bot to manage games. Needs to be hosted by one of the players.')
try:
    with open("config.json") as c:
        config = json.load(c)
except FileNotFoundError:
    print("Config file not found! exiting...")
    sys.exit(-1)

@bot.event
async def on_ready():
    print(f'\n\nLogged in as: {bot.user.name} - {bot.user.id}\nVersion: {discord.__version__}\n')
    bot.main_server = discord.utils.get(bot.guilds, id = config["GUILD"])

    await bot.change_presence(activity=discord.Game(name='Among Us', type=1, url='https://github.com/architdate/Sabotage'))
    print(f'Successfully logged in and booted...!')

if __name__ == '__main__':
    for extension in initial_extensions:
        bot.load_extension(extension)

bot.run(config['TOKEN'], bot=True, reconnect=True)