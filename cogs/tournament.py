from discord.ext import commands
import uuid
from utils import api

class Tournament(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self.bot.user.name} has connected to Discord!')


    @commands.command(name='ranking', help='Print ranking of active tournament')
    #@commands.has_role('nonexisting')
    async def ranking(self,ctx):
        mimir_url = str(ctx.mimir_url)+"eid"+str(ctx.tourney)
        json_body ={ "jsonrpc": "2.0", "method": "getRatingTable", "params": { "eventIdList": [str(mimir_url)], "orderBy": "rating", "order": "desc", "withPrefinished": "false" }, "id": str(uuid.uuid4()) }
        print(json_body)
        response = api.poll_mimir(mimir_url, json_body)
        if response[0] == 200:
           message_content = '```'
           for rank in response[1]['result']:
             message_content += str(rank['display_name'])
             message_content += '\n'
             message_content += str(rank['rating'])
             message_content += '\n'
           message_content += '```' 
           emoji = '\N{THUMBS UP SIGN}'
           await ctx.message.add_reaction(emoji)
        await ctx.send(message_content)


    @commands.command(name='addgame', help='Adds an online game by tenhou url to the active tournament')
    #@commands.has_role('nonexisting')
    async def addgame(self,ctx, game_url):
        mimir_url = str(ctx.mimir_url)+"eid"+str(ctx.tourney)
        json_body = { "jsonrpc": "2.0", "method": "addOnlineReplay", "params": { "eventId": int(ctx.tourney), "link": game_url }, "id": str(uuid.uuid4()) }
        print(json_body)
        response = api.poll_mimir(mimir_url, json_body)
        if response[0] == 200 and "error" not in response[1]:
           emoji = '\N{THUMBS UP SIGN}'
           print(response[1])
           await ctx.message.add_reaction(emoji)
        else: 
           emoji = '\N{CROSS MARK}'

           print(response[1])
           await ctx.message.add_reaction(emoji)
           await ctx.send(response[1]['error']['message'])

def setup(bot):
    bot.add_cog(Tournament(bot))