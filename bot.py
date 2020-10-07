# bot.py
import os
import random
import logging
from discord.ext import commands
from dotenv import load_dotenv

#load env variables from .env file
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
MIMIR_URL=os.getenv('MIMIR_URL')
TOURNEY=os.getenv('TOURNEY')

#configure logging
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


#instanciate bot and define commands
bot = commands.Bot(command_prefix='!')

bot.load_extension("cogs.tournament")
bot.load_extension("cogs.jansou")

#bot.add_cog(Tournament)
bot.run(TOKEN)
