import random
import requests
import xml.etree.ElementTree as ET

class Singleton(type):
    _instances = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class Player():
    def __init__(self):
        self.name = None
        self.score = None
        self.shugi = None
        self.payout = None
        self.calc = ""

    def __str__(self):
        return f"{self.name} {self.score} {self.shugi} {self.payout}"

class TableRate():

    def __init__(self, rate=0.3, shugi=.50, target=30000, start=25000, uma=[30,10,-10,-30]):
        self.rate = rate
        self.shugi = shugi
        self.oka = (target - start) * 4
        self.target = target
        self.start = start
        self.uma = uma

    def __eq__(self, other):
        return (self.rate == other.rate and self.shugi == other.shugi and self.oka == other.oka and self.target == other.target and self.start == other.start and self.uma == other.uma)

    def __str__(self):
        return f"Rate: {self.rate}, Start: {self.start}, Target: {self.target}, Shugi: {self.shugi}, Oka: {self.oka}, Uma: {self.uma}"

# default values rate=0.3, shugi=.50, target=30000, start=25000, uma=[30,10,-10,-30]    
TENSAN = TableRate()
TENGO = TableRate(rate=0.5, shugi=1)
TENPIN = TableRate(rate=1, shugi=2)

class GameInstance(metaclass=Singleton):
    
    def __init__(self):
        self.MAX_PLAYERS = 4 # WARNING NEVER EVER SET TO 3!
        self.waiting = []
        self.pWaiting = [] # Priority waiting
        self.lastError = ""
        self.lastScore = ""

    def reset(self):
        self.waiting = []
        self.pWaiting = []         
        self.lastError = ""
        self.lastScore = ""
        
    def addWaiting(self, name):
        if name in self.waiting or name in self.pWaiting:
            self.lastError = f"{name} is already waiting"
            return 1
        self.waiting.append(name)
        return 0
        
    def removeWaiting(self, name):
        if name in self.waiting or name in self.pWaiting:
            self.waiting.remove(name)
            return 0
        self.lastError = f"{name} is not currently waiting"
        return 1

    def shuffle(self):
        ret = {}        
        if len(self.waiting) >= self.MAX_PLAYERS:
            random.shuffle(self.waiting)
            while(len(self.waiting) >= self.MAX_PLAYERS):
                count = 0
                while(count in ret.keys()):
                    count += 1
                if not count in ret:
                    ret[count] = []
                for i in range(self.MAX_PLAYERS):
                    ret[count].append(self.waiting.pop())
        return ret


    def scoreTable(self, players, tableRate):

        players.sort(key=lambda x: x.score,reverse=True)
        self.lastScore = ""
        
        self.lastScore += f"{tableRate}\n\n"
        self.lastScore += f"All players begin with **Start**[{tableRate.start}] points and pay the difference of the **Target**[{tableRate.target}] to first place\n" 
        self.lastScore += f"So first place gets an **Oka** of ({tableRate.start} - {tableRate.target}) × {self.MAX_PLAYERS} = {(tableRate.target - tableRate.start)*self.MAX_PLAYERS}\n\n"
        self.lastScore += f"A **Rate** of {tableRate.rate} means each 1000 points is ${tableRate.rate:.2f}\n\n"
        
        oka = [tableRate.oka] + [0]*self.MAX_PLAYERS # giving 1st place oka bonus
        for i, p in enumerate(players):
            self.lastScore += f"#{i+1}Place: (Score[{p.score}] + Oka[{oka[i]}] - Target[({tableRate.target}])/1000) × Rate[{tableRate.rate}] = ${((p.score + oka[i] - tableRate.target)/1000)*tableRate.rate:.2f}\n"

        self.lastScore += "\n"            
        self.lastScore += f"**Uma** of {tableRate.uma} is also applied based on position, and multiplied by the table **Rate**[{tableRate.rate}]\n"

        for i, p in enumerate(players):
            self.lastScore += f"#{i+1}Place: ${tableRate.rate*tableRate.uma[i]}\n"
        
        self.lastScore += "\n"
        self.lastScore += f"Finally the **Shugi Rate**[{tableRate.shugi}] is multiplied by the number of shugi and added to the final score\n"
        
        for i,p in enumerate(players):
            self.lastScore += f"#{i+1}Place: Shugi rate[{tableRate.shugi}] × Player Shugi[{p.shugi}] = {tableRate.shugi * p.shugi}\n"

        self.lastScore += "\n"
        self.lastScore += "Finally\n"

        
        for i, p in enumerate(players):

            shugi = tableRate.shugi * p.shugi
            calc = (((p.score + oka[i] - tableRate.target)/1000) + tableRate.uma[i]) * tableRate.rate + shugi
            p.payout = round(calc,2)
            self.lastScore += f"#{i+1}Place: (((({p.score}+{oka[i]}-{tableRate.target})/1000)+{tableRate.uma[i]})×{tableRate.rate}+{tableRate.shugi}×{p.shugi}) = ${p.payout}\n"

        return players


    def parseGame(self, log, rate=TENSAN):

        if "https://" in log.lower() or "http://" in log.lower():
            log = log.split("=")[1].split("&")[0]
        xml = requests.get("http://tenhou.net/0/log/?"+log).text
        print("Prasing http://tenhou.net/0/log/?"+log)

        def convertToName(s):
            ret = bytes()
            for c in s.split("%")[1:]:
                ret +=  int(c,16).to_bytes(1,"little")
            return ret.decode("utf-8")

        players = [Player() for i in range(4)]

        root = ET.fromstring(xml)

        type_tag = root.find('UN')
        players[0].name = convertToName(type_tag.get('n0'))
        players[1].name = convertToName(type_tag.get('n1'))
        players[2].name = convertToName(type_tag.get('n2'))
        players[3].name = convertToName(type_tag.get('n3'))

        owari = None
        for type_tag in root.findall('AGARI'):
            owari = type_tag.get("owari")
            if owari == None:
                continue
            break

        if owari == None:
            for type_tag in root.findall('RYUUKYOKU'):
                owari = type_tag.get("owari")
                if owari == None:
                    continue
                break

        if owari == None:
            self.lastError = f"Failed to parse :< Please complain to moku"
            return None            
            
            
        owari = owari.split(",")
        # @TODO check if there is shugi

        if len(owari) >= 8:
            owari += [0,0,0,0,0,0,0,0]
        for i in range(0,4):
            players[i].score = int(owari[i*2])*100
            players[i].shugi = int(owari[i*2+8])


        return self.scoreTable(players, rate)

