# bot.py
import os
import random
import requests
import uuid
import json

from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
MIMIR_URL=os.getenv('MIMIR_URL')
TOURNEY=os.getenv('TOURNEY')

#helper function to talk to mimir rest api
def poll_mimir(url, json_body):
   r = requests.get(url=url, data=json.dumps(json_body)) 
   return r.status_code, r.json()


#instanciate bot and define commands
bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

@bot.command(name='ranking', help='Print ranking of active tournament')
#@commands.has_role('nonexisting')
async def ranking(ctx):
    mimir_url = str(MIMIR_URL)+"eid"+str(TOURNEY)
    json_body ={ "jsonrpc": "2.0", "method": "getRatingTable", "params": { "eventIdList": [str(TOURNEY)], "orderBy": "rating", "order": "desc", "withPrefinished": "false" }, "id": str(uuid.uuid4()) }
    print(json_body)
    response = poll_mimir(mimir_url, json_body)
    if response[0] == 200:
       print(response[1]) 
       emoji = '\N{THUMBS UP SIGN}'
       await ctx.message.add_reaction(emoji)
    await ctx.send(response)

@bot.command(name='addgame', help='Adds an online game by tenhou url to the active tournament')
#@commands.has_role('nonexisting')
async def addgame(ctx, game_url):
    mimir_url = str(MIMIR_URL)+"eid"+str(TOURNEY)
    json_body = { "jsonrpc": "2.0", "method": "addOnlineReplay", "params": { "eventId": int(TOURNEY), "link": game_url }, "id": str(uuid.uuid4()) }
    print(json_body)
    response = poll_mimir(mimir_url, json_body)
    if response[0] == 200 and "error" not in response[1]:
       emoji = '\N{THUMBS UP SIGN}'
       print(response[1])
       await ctx.message.add_reaction(emoji)
    else: 
       emoji = '\N{CROSS MARK}'

       print(response[1])
       await ctx.message.add_reaction(emoji)
       await ctx.send(response[1]['error']['message'])
       

bot.run(TOKEN)
