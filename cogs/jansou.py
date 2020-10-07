from discord.ext import commands
from utils import gi
import copy

game = gi.GameInstance()

class Jansou(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def score(self, ctx, log=None, rate="tensan", shugi=None):
        """
        Score a game log for jansou rules (Results in units)
        Args:
            log:
                A full url or just the log id
            rate (optional):
                tensan(default), tengo, or tenpin
            shugi (optional):
                defaults to the rate shugi
        """


        gi.player = ctx.author
        chan = ctx.channel

        if log == None or rate == None:
            await chan.send("usage: !score [tenhou_log] [rate]\nEx: !score https://tenhou.net/0/?log=2020051313gm-0209-19713-10df4ad2&tw=1 tengo")


        table = [["Score","","Pay","Name"]]

        rate = rate.lower()
        tableRate = None

        if rate == "tensan" or rate == "0.3" or rate == ".3":
            tableRate = copy.deepcopy(gi.TENSAN)
        elif rate == "tengo" or rate == "0.5" or rate == ".5":
            tableRate = copy.deepcopy(gi.TENGO)
        elif rate == "tenpin" or rate == "1.0":
            tableRate = copy.deepcopy(gi.TENPIN)
        else:
            await chan.send(f"{rate} is not a valid rate (try !help score)")
            return

        if(shugi != None):
            try:
                tableRate.shugi = round(float(shugi),3)
            except:
                await chan.send(f"{shugi} is not a valid shugi")
                return

        players = game.parseGame(log, tableRate)


        for p in players:
            score = str(p.score)
            shugi = str(p.shugi)
            payout = str(p.payout)
            #if not "-" in score:
            #    score = "+"+score
            if not "-" in shugi:
                shugi = "+"+shugi
            if not "-" in payout:
                payout = "+"+payout       
            table.append([str(score),str(shugi),str(payout),str(p.name)])

        colMax = [max([len(i) for i in c]) for c in zip(*table)]
        colMax[-1] = 0

        ret = f"```{tableRate}\n"
        for row in table:
            for i,col in enumerate(colMax):
                ret += row[i].ljust(col+1)
            ret += "\n"
        ret += "```"

        for guild in ctx.bot.guilds:
            for log_chan in guild.text_channels:
                if str(log_chan) == "daily-log":
                    print("found")
                    await log_chan.send(log)
                    await log_chan.send(ret)

        await chan.send(ret)

def setup(bot):
    bot.add_cog(Jansou(bot))