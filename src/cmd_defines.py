from src.command import Command
import src.objects as o
from src.geometry import Point

class AllCommands:
    '''Container for all commands'''

    ################################
    # FOR ALL CONTROLLABLES
    ################################

    ################################
    def _dmg_self_inst(session, actor):
        actor.heal_pts -= 3
        if actor.heal_pts <= 0:
            actor.destroy(actor)
    def _dmg_self_deld(session, actor):
        actor.heal_pts -= 7
        if actor.heal_pts <= 0:
            actor.destroy(actor)
    def _dmg_self_ireq(session, actor):
        return (True if actor.heal_pts > 10 else False), 'heal_pts'
    dmg_self = Command(_dmg_self_inst, _dmg_self_deld,
        grouped=True, queueable=True, duration=60,
        instant_reqs=[_dmg_self_ireq])

    ################################
    # FOR OBJECT TYPES
    ################################

    ################################
    def _move_inst(session, actor, coords):
        actor.dest = Point(*coords)
        actor.request_path()
    def _move_end(scmd):
        actor = scmd.actor
        return True if actor.coords == actor.dest else False
    move = Command(_move_inst, None,
        grouped=True, queueable=True, end=_move_end,
        takes_pt=True)


    ################################
    # FOR SPECIFIC OBJECTS
    ################################

    ################################
    def _train_worker_deld(session, actor, coords):
        obj = o.Worker(session, Point(*coords), actor.owner)
        session.add_object(obj)
    train_worker = Command(None, _train_worker_deld,
        grouped=False, queueable=True, cost=(50,0,0), duration=45,
        takes_pt=True)
    ################################
    def _train_soldier_deld(session, actor, coords):
        obj = o.Soldier(session, Point(*coords), actor.owner)
        session.add_object(obj)
    train_soldier = Command(None, _train_soldier_deld,
        grouped=False, queueable=True, cost=(100,0,0), duration=90,
        takes_pt=True)
