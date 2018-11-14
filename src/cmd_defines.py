from src.command import Command, StartedCommand
import src.objects as o
from src.geometry import Point

class AllCommands:
    '''Container for all commands'''

    ################################################################
    # For all Controllables

    ################################
    # CONTROLLABLE: Cancel
    def _cancel_inst(session, actor):
        if actor.queue != []:
            del actor.queue[-1]
        else:
            actor.current = StartedCommand.placeholder()
        actor.busy = False
    cancel = Command(_cancel_inst, None,
        grouped = False, queueable=False, duration=0)

    ################################################################
    # For Units

    ################################
    # UNIT: Move
    def _move_inst(session, actor, coords):
        actor.dest = Point(*coords)
        actor.request_path()
    def _move_end(scmd):
        actor = scmd.actor
        return True if actor.coords == actor.dest else False
    move = Command(_move_inst, None,
        grouped=True, queueable=False, end=_move_end,
        takes_pt=True)

    ################################
    # UNIT: Stop movement
    def _stop_inst(session, actor):
        actor.dest = actor.coords.copy()
        actor.node = Point(-1, -1)
        actor.nodes = []
        actor.direction = Point(0, 0)
    stop = Command(_stop_inst, None,
        grouped=True, queueable=False, duration=0)


    ################################################################
    # For specific objects

    ################################
    # COMMAND: Train worker
    def _train_worker_deld(session, actor, coords):
        obj = o.Worker(session, Point(*coords), actor.owner)
        session.add_object(obj)
    train_worker = Command(None, _train_worker_deld,
        grouped=False, queueable=True, cost=(50,0,0), duration=45,
        takes_pt=True)

    ################################
    # COMMAND: Train soldier
    def _train_soldier_deld(session, actor, coords):
        obj = o.Soldier(session, Point(*coords), actor.owner)
        session.add_object(obj)
    train_soldier = Command(None, _train_soldier_deld,
        grouped=False, queueable=True, cost=(100,0,0), duration=90,
        takes_pt=True)
