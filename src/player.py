class Player:
    def __init__(self, name, pwd):
        self.username = name
        self.clr_choice = 'green'

    def add_to_session(self, session):
        self.session = session
        self.color = session.get_color(self)
        self.blnd_count = 0
        self.unit_count = 0
        self.rsrc_wood = session.app.GAME.starting_wood
        self.rsrc_iron = session.app.GAME.starting_iron
        self.rsrc_fuel = session.app.GAME.starting_fuel
