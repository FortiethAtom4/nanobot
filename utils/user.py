import datetime, random

class User:
    xp_cooldown: datetime.timedelta = datetime.timedelta(seconds=60) #seconds to wait until next xp gain

    def __init__(self, name):
        self.name: str = name
        self.level: int = 0
        self.xp_current: int = 0
        self.xp_total: int = 0
        self.total_messages: int = 0
        self.cooldown: datetime.datetime = datetime.datetime(2001,1,16)

    def get_level_req(self):
        # not sure how python does pemdas
        # 5 * (lvl ^ 2) + (50 * lvl) + 100 - xp <- mee6 function to determine how much XP is required to level up
        return 5* (self.level ** 2) + (50 * self.level) + 100
    
    def level_up(self):
        self.xp_current = self.xp_current - self.get_level_req()
        self.level += 1
    
    # Grants experience to the user using Mee6's method. Levels them up as needed.
    def gain_xp(self, value: int = -1) -> bool:
        cooldown_time: datetime.timedelta = self.cooldown + User.xp_cooldown
        cooldown: datetime.timedelta = datetime.datetime.now() + datetime.timedelta(seconds=0)
        levelup = False
        if cooldown > cooldown_time:
            self.total_messages += 1
            if value == -1:
                value = random.randint(15,25) 
            self.cooldown = datetime.datetime.now()
            self.xp_current += value
            self.xp_total += value
           
            while self.xp_current >= self.get_level_req():
                levelup = True
                self.level_up()
        return levelup