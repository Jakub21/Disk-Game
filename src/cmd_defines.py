from src.command import Command, StartedCommand
import src.objects as o
from src.geometry import Point

class AllCommands:
    '''Container for all commands'''
    def __init__(self):
        ################################################################
        # For all Controllables

        ################################
        # CONTROLLABLE: Cancel
        def _cancel_inst(session, actor):
            torefund = None
            if actor.queue != []:
                #torefund = actor.queue[-1][0].cost # NOTE: Uncomment when player
                    # will be charged at command-click, not -start
                del actor.queue[-1]
            else:
                if not actor.current.is_placeholder:
                    torefund = actor.current.command.cost
                    actor.current = StartedCommand.placeholder()
                    actor.busy = False
            if torefund is not None:
                owner = actor.owner
                owner.refund_rsrc(torefund)
        self.cancel = Command('cancel', _cancel_inst, None,
            grouped=False, queueable=False, duration=0)

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
        self.move = Command('move', _move_inst, None,
            grouped=True, queueable=False, end=_move_end,
            takes_pt=True, cost=(0,0,0))

        ################################
        # UNIT: Stop movement
        def _stop_inst(session, actor):
            actor.dest = actor.coords.copy()
            actor.node = Point(-1, -1)
            actor.nodes = []
            actor.direction = Point(0, 0)
        self.stop = Command('stop', _stop_inst, None,
            grouped=True, queueable=False, duration=0)


        ################################################################
        # For specific objects

        ################################
        # COMMAND: Train worker
        def _train_worker_deld(session, actor, coords):
            obj = o.Worker(session, Point(*coords), actor.owner)
            session.add_object(obj)
        self.train_worker = Command('train_worker', None, _train_worker_deld,
            grouped=False, queueable=True, cost=(50,0,0), duration=22,
            takes_pt=True)

        ################################
        # COMMAND: Train soldier
        def _train_soldier_deld(session, actor, coords):
            obj = o.Soldier(session, Point(*coords), actor.owner)
            session.add_object(obj)
        self.train_soldier = Command('train_soldier', None, _train_soldier_deld,
            grouped=False, queueable=True, cost=(100,0,0), duration=45,
            takes_pt=True)
