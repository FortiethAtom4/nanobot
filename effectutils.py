# Class which stores ability information.
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class Ability():
    def __init__(self, name: str, display_name: str, description: str, value: int = 0, uses: int = 0, properties: dict = {}):

        # name will be used for ability recognition, display_name will be what the player actually sees
        self.name = name
        self.display_name = display_name

        self.description = description
        self.value = value
        self.uses = uses

        # this dict will be used to store data for abilities with unique parameters.
        self.properties = properties

    # Adding/removing properties on an ability during runtime. 
    # Not sure how useful these will be, but could add some fun mechanics.
    def set_property(self, pname: str, pvalue):
        self.properties[pname] = pvalue

    def delete_property(self, pname: str):
        del self.properties[pname]



# Class which stores/manipulates effects (i.e. buffs and debuffs).
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class Effect(Ability):
    def __init__(self, name: str, display_name: str, description: str, value: int = 0, uses: int = 0, properties: dict = {}):
        super().__init__(name, display_name, description, value, uses, properties)