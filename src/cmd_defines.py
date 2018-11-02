from src.command import Command

def cmd_dmg_self(actor):
    actor.heal_pts -= 10
    if actor.heal_pts <= 0:
        actor.destroy(actor)

class AllCommands:
    '''Container class'''
    dmg_self = Command(cmd_dmg_self, True, duration=30)
