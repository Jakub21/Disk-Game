'''
Commands end:
- immediatelly
- after set amount of ticks
- on trigger
This is defined by 'end' parameter
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
        end [int/func/lambda] When command ends
        hard [bool] True if command is hard, False if soft
        pre [Command](None) Command to execute before this one.
            Has to be uninterrupted to start main function
        post [Command](None) Command to execute after this one
        takes_pt [bool](False) Commands takes board coords as param when exec.
        takes_obj [bool](False) Command takes board object as param when exec.
        param_valid [func/lambda] Function that checks is exe-time parameter
            is valid
        prereqs [func/lambda list] Requirements needed to start PRE
            Parameters must return booleans
        reqs [func/lambda list] Requirements needed to start the command
            Parameters must return booleans
        reqs []
    '''
    def __init__(self, method, end, hard, pre=None, post=None,
            takes_pt=False, takes_obj=False, param_valid=None, prereqs=[],
            reqs=[]):
        if takes_pt and takes_obj:
            raise ValueError('Command can not need both Point and Object')
        self.method = method
        self.end = end
        self.hard = hard
        self.pre = pre
        self.post = post
        self.takes_pt = takes_pt
        self.takes_obj = takes_obj
        self.param_valid = param_valid
        self.prereqs = prereqs
        self.reqs = reqs

    def execute(self, objlist, *args):
        '''
        objlist [Controllable list] Objects which execute command
        '''
        for actor in objlist:
            for req in self.prereqs:
                if not req: return
            if self.pre is not None:
                self.pre.execute(actor, *args)
            for req in self.reqs:
                if not req: return
            self.method(actor, *args)
            if self.post is not None:
                self.post.execute(actor, *args)
