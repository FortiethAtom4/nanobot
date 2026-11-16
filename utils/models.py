import datetime, random, logging
logger = logging.getLogger(__name__)

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import BigInteger, Boolean, Integer, String, DateTime

from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

class OldUser(Base):
    __tablename__ = "old_users"

    xp_cooldown: datetime.timedelta = datetime.timedelta(seconds=60) #seconds to wait until next xp gain

    name: Mapped[str] = mapped_column(String, primary_key=True)
    level: Mapped[int] = mapped_column(Integer)
    xp_current: Mapped[int] = mapped_column(Integer)
    xp_total: Mapped[int] = mapped_column(Integer)
    total_messages: Mapped[int] = mapped_column(Integer)
    cooldown: Mapped[datetime.datetime] = mapped_column(DateTime)
    found: Mapped[int] = mapped_column(Integer,default=0)

    def __init__(self, name: int):
        self.name: str = name
        self.level: int = 0
        self.xp_current: int = 0
        self.xp_total: int = 0
        self.total_messages: int = 0
        self.cooldown: datetime.datetime = datetime.datetime(2001,1,16)
        self.found = 0

class User(Base):
    __tablename__ = "users"

    xp_cooldown: datetime.timedelta = datetime.timedelta(seconds=60) #seconds to wait until next xp gain

    server_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    level: Mapped[int] = mapped_column(Integer)
    xp_current: Mapped[int] = mapped_column(Integer)
    xp_total: Mapped[int] = mapped_column(Integer)
    total_messages: Mapped[int] = mapped_column(Integer)
    cooldown: Mapped[datetime.datetime] = mapped_column(DateTime)

    def __init__(self, server_id: int, user_id: int, name: int):
        self.server_id: int = server_id
        self.user_id: int = user_id
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

class Timer(Base):

    __tablename__ = "timers"

    timer_id: Mapped[int] = mapped_column(Integer,primary_key=True,autoincrement=True)

    server_id: Mapped[int] = mapped_column(BigInteger)
    user_id: Mapped[int] = mapped_column(BigInteger)
    channel_id: Mapped[int] = mapped_column(BigInteger)
    message_id: Mapped[int] = mapped_column(BigInteger, nullable=True)

    end_time: Mapped[datetime.datetime] = mapped_column(DateTime)
    pause_time: Mapped[datetime.datetime] = mapped_column(DateTime,nullable=True)
    stopped: Mapped[bool] = mapped_column(Boolean)

    def __init__(self,server_id: int, user_id: int, channel_id: int):
        self.server_id = server_id
        self.user_id = user_id
        self.channel_id = channel_id

        self.cur_time: datetime.datetime = datetime.datetime.now() 
        self.end_time: datetime.datetime = datetime.datetime.now() 
        self.pause_time: datetime.datetime = None
        self.stopped = True

    def set_message_id(self,message_id: int):
        self.message_id = message_id

    def start(self,end_time: datetime.timedelta):
        if not self.stopped:
            return False
        self.end_time = datetime.datetime.now() + end_time
        self.stopped = False
        return True

    # returns true if time is up, else false
    def increment(self) -> bool | None:
        self.cur_time = datetime.datetime.now()
        if self.cur_time >= self.end_time:
            self.stopped = True
            self.pause_time = None
        
        return self.stopped

    # returns true if self.stopped is already true, else false
    def pause(self):
        if self.stopped:
            return True
        self.pause_time = datetime.datetime.now()
        self.stopped = True
        return False

    # returns false if self.stopped is already false, else true
    def unpause(self) -> bool:
        if not self.stopped:
            return False
        temp_unpause_delta: datetime.timedelta = self.end_time - self.pause_time
        self.end_time = datetime.datetime.now() + temp_unpause_delta
        self.stopped = False
        self.pause_time = None
        return True
    
    def stop(self) -> bool:
        if self.paused_or_stopped() != 0:
            self.stopped = True
            self.end_time = datetime.datetime.now()
            self.pause_time = None
            return True
        return False
    
    def toggle(self):
        if self.stopped:
            return self.unpause()
        return self.pause()
    
    def add_time(self,hours: int, minutes: int):
        time_added = datetime.timedelta(hours=hours,minutes=minutes)
        self.end_time += time_added
        self.increment() # updates self.stopped if subtracted time goes over time limit
        return time_added
    
    # returns 0 if stopped, 1 if paused, 2 if running
    def paused_or_stopped(self) -> 0 | 1 | 2:
        if self.stopped:
            if self.pause_time == None:
                return 0
            return 1
        return 2
    
    def __str__(self):
        return str(datetime.timedelta(seconds=int((self.end_time - self.cur_time).total_seconds())))

    def __repr__(self):
        return self.__str__()