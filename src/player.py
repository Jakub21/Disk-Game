class Player:
    def __init__(self, name, pwd):
        self.username = name
        self.clr_choice = 'green'

    def add_to_session(self, session):
        self.session = session
        self.color = session.get_color(self)
        self.blnd_count = 0
        self.unit_count = 0
        self.r_wood = session.app.GAME.starting_wood
        self.r_iron = session.app.GAME.starting_iron
        self.r_fuel = session.app.GAME.starting_fuel

    def defeat(self):
        self.session.rem_player(self)

    def leave_session(self):
        del self.session
        del self.color
        del self.blnd_count
        del self.unit_count
        del self.r_wood
        del self.r_iron
        del self.r_fuel

    def check_rsrc(self, resources):
        wood, iron, fuel = resources
        if wood > self.r_wood:
            return False, 'wood'
        if iron > self.r_iron:
            return False, 'iron'
        if fuel > self.r_fuel:
            return False, 'fuel'
        return True, None

    def charge_rsrc(self, resources):
        wood, iron, fuel = resources
        self.r_wood -= wood
        self.r_iron -= iron
        self.r_fuel -= fuel

    def refund_rsrc(self, resources):
        wood, iron, fuel = resources
        self.r_wood += wood
        self.r_iron += iron
        self.r_fuel += fuel
