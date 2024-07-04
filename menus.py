import discord
from discord.ui import Select
import db

class characterSelect(Select):
    def __init__(self):
        super().__init__(
            placeholder="Choose a class from the selection.",
            min_values=1,
            max_values=1,
            options=[
                discord.SelectOption(
                    label="Warrior",
                    value="Warrior",
                    description="stub"
                ),
                discord.SelectOption(
                    label="Ranger",
                    value="Ranger",
                    description="stub"
                ),
                discord.SelectOption(
                    label="Mage",
                    value="Mage",
                    description="stub"
                ),
                discord.SelectOption(
                    label="General",
                    value="General",
                    description="stub"
                ),
                discord.SelectOption(
                    label="Trickster",
                    value="Trickster",
                    description="stub"
                )
            ]
        )

    async def callback(self, interaction: discord.Interaction):
        resp_string = f"You chose {self.values[0]}."
        # attempt to insert a new user
        newplayer = db.insert_new_user(interaction.user.name,self.values[0])
        if newplayer == -1:
            # await interaction.response.send_message("You already have a character!")
            resp_string += "\nYou already have a character!"
        else:
            resp_string+= f'''\nSuccessfully created a new character for {interaction.user.name}!
Class: {newplayer.pclass}
HP: {newplayer.maxhp[0]}
ATK: {newplayer.atk[0]}
Defense: {newplayer.defense[0] * 100}%'''
        await interaction.respond(resp_string)
        

    