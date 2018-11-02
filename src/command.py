'''
Commands end:
- immediatelly
- after set amount of ticks
- on trigger
This is defined by 'end' and 'duration' parameters
Commands can be soft or hard. Soft commands can be executed while hard one
is in progress. If a command is added with out Shift, all other soft
commands are cancelled. If a hard command is added while other hard
command is running, the added command is added to the commands queue.
<When more objects in selection>
If command is hard it is only executed by one unit
else by every object that can
'''

class Command:
    '''Command class
    Parameters:
        method [func] Main command function
        hard [bool] True if command is hard, False if soft
        duration [int] Duration of the command
        end [func/lambda] When command ends
        pre [Command](None) Command to execute before this one.
            Has to be uninterrupted to start main function
        post [Command](None) Command to execute after this one
        takes_pt [bool](False) Commands takes board coords as param when exec.
        takes_obj [bool](False) Command takes board obj as param when exec.
        param_valid [func/lambda] Function that checks is exe-time parameter
            is valid
        prereqs [func/lambda list] Requirements needed to start PRE
            Parameters must return booleans
        reqs [func/lambda list] Requirements needed to start the command
            Parameters must return booleans
        get_perc [func/lambda] Function that returns progress percentage
        is both duration and end-conditions are set an exception will be raised
    '''
    def __init__(self, method, hard, duration=0, end=None, pre=None, post=None,
            takes_pt=False, takes_obj=False, param_valid=None, prereqs=[],
            reqs=[], get_perc=None):
        if takes_pt and takes_obj:
            raise ValueError('Command can not need both Point and Object')
        if duration != 0 and end is not None:
            raise ValueError('Can not set both end-conditions and duration')
        self.method = method
        self.hard = hard
        self.end = end
        self.duration = duration
        self.pre = pre
        self.post = post
        self.takes_pt = takes_pt
        self.takes_obj = takes_obj
        self.param_valid = param_valid
        self.prereqs = prereqs
        self.reqs = reqs
        self.get_perc = get_perc
        self.can_perc = not get_perc is None

    def start(self, objlist, *args):
        '''
        objlist [Controllable list] Objects which execute command
        '''
        if self.hard:
            obj = objlist[0] # TODO: Object that can exe command earliest
            return self.queue(obj, *args)
        else:
            for actor in objlist:
                self.execute(actor, *args)

    def queue(self, object, *args):
        object.queue_cmd(self, args)

    def execute(self, actor, *args):
        for req in self.prereqs:
            if not req: return
        if self.pre is not None:
            self.pre.execute(actor, *args)
        for req in self.reqs:
            if not req: return
        self.method(actor, *args)
        if self.post is not None:
            self.post.execute(actor, *args)



class StartedCommand:
    def __init__(self, session, actor, command, *args):
        self.is_placeholder = False
        self.session = session
        self.actor = actor
        self.command = command
        self.args = args
        self.start_tick = self.session.tick

    @classmethod
    def placeholder(self):
        self.is_placeholder = True

    def check_done(self):
        if self.command.duration != 0:
            return self.session.tick == self.command.duration + self.start_tick
        else:
            return self.command.end(self)

    def exec_cmd(self):
        self.command.execute(self.actor, *self.args)
