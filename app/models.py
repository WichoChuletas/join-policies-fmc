class UserData:
    def __init__(self, username, password):
        self.username = username
        self.password = password

class AccessControlPolicyData:
    def __init__(self, name, rules):
        self.name = name
        self.rules = rules