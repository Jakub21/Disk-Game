class Weapon:
    '''Create a weapon
    Init Parameters:
        damage [int] How much damage this weapon deals
        rate [int] How much ticks it takes for this weapon to prepare for
            next shoot
        range [int] Range of the weapon
        ignore_armor [bool] If this weapon ignores armor (armor value is not
            substracted from damage amount)
    Other attributes:
        is_placeholder [bool] Set to true if a weapon deals no damage
        cooldown [int] In how many ticks a weapon will be able to shoot again
        is_ready [bool] Set to true if cooldown has reached 0
    '''
    def __init__(self, damage=0, rate=0, range=0, ignore_armor=False):
        self.damage, self.rate, self.range = damage, rate, range
        self.ignore_armor = ignore_armor
        self.cooldown = 0
        self.is_placeholder = False
        self.is_ready = True
        if damage == 0:
            self.is_placeholder = True

    def cooldown(self, target):
        '''Deal damage to target object'''
        if self.is_ready:
            self.cooldown = self.rate

    def get_cd_frac(self):
        '''Get percentage of cooldown (low - almost ready, high - just used)'''
        return self.cooldown / self.rate

    def update(self):
        '''Update cooldown every game tick'''
        if self.cooldown > 0:
            self.cooldown -= 1
        if self.cooldown == 0 and not self.is_ready:
            self.is_ready = True
