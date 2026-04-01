from utils.user import User


class Server:

    def __init__(self):
        self.users: list[User] = []

    def get_user(self, name:str):
        return next((user for user in self.users if user.name == name),None)
    
    