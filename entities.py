# User stats:
# ID
# name
# Class (decide on some classes)
# Subclass (starts as N/A)
# level
# HP
# ATK
# DEF

# classes:
# Warrior (Knight, Berserker)
# Mage (Elementalist, Spiritualist)
# Ranger (Thief, Trapper)
# General (Necromancer, Tinkerer)
# Trickster

# The parent class of all entities in this game.
# Instantiates some default values; subclasses will overwrite them.
# Will include some methods all entities will share, such as attacking and ability usage.

from collections import namedtuple

class Entity:
    def __init__(self,name):
        self.pclass = ""
        self.psubclass = ""
        self.name=name
        self.xp = 0
        self.level = 1
        self.equipped_abilities = []
        self.other_abilities = []

        # The first number is the actual stat value. The second is the stat's scaling with level.
        self.currenthp = 0
        self.maxhp = [0,0]
        self.atk = [0,0]

        # a decimal value from 0 to 1
        self.defense = [0,0]

        # Currency for getting abilities. 
        self.coins = 0

    # copy values from database to create a new Entity.
    def init_from_dict(self,pclass,psubclass,xp,level,equipped_abilities,other_abilities,currenthp,maxhp,atk,defense,coins):
        self.pclass = pclass
        self.psubclass = psubclass
        self.xp = xp
        self.level = level
        self.equipped_abilities = equipped_abilities
        self.other_abilities = other_abilities
        self.currenthp = currenthp
        self.maxhp = maxhp
        self.atk = atk
        self.defense = defense
        self.coins = coins

        return self

    # the following functions initialize the entity as different player classes.
    def init_warrior(self):
        self.pclass = "Warrior"
        self.psubclass = ""
        self.maxhp = [20,5]
        self.atk = [3,1]
        self.defense = [0.1,0.005]
        self.currenthp = self.maxhp[0]

    def init_mage(self):
        self.pclass = "Mage"
        self.psubclass = ""
        self.maxhp = [15,1]
        self.atk = [3,1]
        self.currenthp = self.maxhp[0]

    def init_ranger(self):
        self.pclass = "Ranger"
        self.psubclass = ""
        self.maxhp = [15,1]
        self.atk = [5,2]
        self.currenthp = self.maxhp[0]

    def init_general(self):
        self.pclass = "General"
        self.psubclass = ""
        self.maxhp = [25,6]
        self.atk = [2,1]
        self.defense = [0,0.005]
        self.currenthp = self.maxhp[0]

    def init_trickster(self):
        self.pclass = "Trickster"
        self.psubclass = ""
        self.maxhp = [25,6]
        self.atk = [5,2]
        self.defense = [0.1,0]
        self.currenthp = self.maxhp[0]

    # attack another Entity.
    def attack(self,target):
        damage_dealt = self.atk * (1 - target.defense)
        # target.hp = 0 if target.hp - damage_dealt <= 0 else target.hp-damage_dealt

    def get_level_req(self):
        return 10 + 2 * ((self.level - 1) ** 2)

    # Use an ability. 
    def use_ability(self,ability_name):
        pass

    # Level up, increasing stats accordingly and returning a level up message.
    # XP function: levelxp = 10 + 2 * (level - 1) ^ 2
    def level_up(self):
        # not sure how closely python follows pemdas
        xp_req = 10 + 2 * ((self.level - 1) ** 2)
        level_up = False

        # this logic is kinda bad, gotta find a better solution
        if self.xp >= xp_req:
            # prepare print statement
            oldlevel = self.level
            oldmaxhp = self.maxhp[0]
            oldatk = self.atk[0]
            olddef = self.defense[0]
            level_up = True

        while self.xp >= xp_req:
            # overflow xp
            self.xp -= xp_req

            self.level += 1
            self.maxhp[0] += self.maxhp[1]
            self.currenthp = self.maxhp
            self.atk[0] += self.atk[1]
            self.defense[0] += self.defense[1]
            xp_req = 10 + 2 * ((self.level - 1) ** 2)
        
        if level_up:
            return f'''Congratulations, {self.name}! You have leveled up!
Level: {oldlevel} >> {self.level}
Maximum HP: {oldmaxhp} >> {self.maxhp[0]}
Attack: {oldatk} >> {self.atk[0]} {f"\nDefense: {round(olddef * 100,2)}% >> {round(self.defense[0] * 100,2)}%" if self.defense[1] > 0 else ""}'''
        else:
            return "XP increased. No levelups detected."


    def test_xp(self):
        self.xp += 1000
        return self.level_up()

# A subclass used for all enemies.
class Enemy(Entity):
    def __init__(self,name,hp,atk,defense,level,abilities,AI_type,xp_reward,coins_reward):
        super().__init__(name)
        self.maxhp = hp
        self.atk = atk
        self.defense = defense
        self.level = level
        self.abilities = abilities
        self.AI_type = AI_type
        self.xp_reward = xp_reward
        self.coins_reward = coins_reward

    # initialization stuff for grunt and other non-specialized enemies goes here.
    def init_no_class_enemy(self):
        self.pclass = "None"
        

# Abilities will be a dict comprised of:
# name
# desc
# value
# num_uses
# 
# If an ability needs other parameters, it will be added to the dict and checked for in the switch statement
# that does ability resolution.
def use_ability(entity: Entity, ability_name: str):
    
    pass


# decoder function used for getting Entities from the database.
def entity_decoder(entity_dict):
    return namedtuple('X', entity_dict.keys())(*entity_dict.values())