class Command:
    def __init__(self, instant=None, delayed=None, grouped=None, queueable=None,
            cost=(0,0,0), duration=None, end=None, post=None, takes_pt=False,
            takes_obj=False, instant_reqs=[], delayed_reqs=[], get_perc=None):
        '''Command Class
        Parameters:
            instant     [func](None) Function executed instantly.
                Params taken: session, actor [point] [object]
            delayed     [func](None) Function executed after End is reached.
                Commands that are not queueable can not have delayed method
                Params taken: session, actor [point] [object]
            cost        [3-int tuple](0,0,0) Amount of resources taken from
                player that started command
            grouped     [bool](None) None - auto based on cost.
                True - All selected units that have this command type added
                will execute it. False - only one unit will execute.
            queueable   [bool](None) None - auto based on Delayed presence
                True - Add to queue. False - Execute instantly.
                forced_queue kw-arg of start method overrides this setting.
            duration    [int](None) None - end param is used instead.
                Delay duration in ticks
            end         [func](None) Must return a boolean. Delay ends when
                this function returns True. Receives StartedCommand instance.
            post        [func](None) Function executed after delayed func ends.
            takes_pt    [bool](False) True - Command takes on-board coordinates
                as parameter and is started when those pointed.
            takes_obj   [bool](False) True - Command takes in-game object
                as parameter and is started when a valid object is pointed
            param_valid [func](None) Function that returns True when exe-time
                parameter is valid. Takes point or object.
            instant_reqs [func list]([]) Requirements that have to be met
                to start instant function. Functions receive session and actor.
            delayed_reqs [func list]([]) Requirements that have to be met
                to start delayed function. Functions receive session and actor.
                Checked instantly.
            get_perc    [func](None) Function that returns completion percentage
                (delay phase). Receives StartedCommand instance.
        '''
        if grouped is None:
            grouped = True if cost == (0,0,0) else False
        if queueable is None:
            queueable = True if delayed is None else False
        if queueable is False and delayed is not None:
            raise ValueError('Non-queueable commands cannot have delayed method')
        if duration is not None and end is not None:
            raise ValueError('Specified both end and duration params')
        if duration is None and end is None:
            raise ValueError('Specify end or duration parameter')
        if takes_pt and takes_obj:
            raise ValueError('Both takes_pt and takes_obj are True')
        self.instant = instant
        self.delayed = delayed
        self.grouped = grouped
        self.queueable = queueable
        self.cost = cost
        self.duration = duration
        self.end = end
        self.post = post
        self.takes_pt = takes_pt
        self.takes_obj = takes_obj
        self.instant_reqs = instant_reqs
        self.delayed_reqs = delayed_reqs
        self.get_perc = get_perc
        self.can_perc = get_perc is not None

    def start(self, session, objlist, *args, forced_queue=False):
        '''objlist [Controllable list] Objects which execute command'''
        if not self.grouped:
            objlist = [objlist[0]] # TODO: Object that can exe command earliest
        if self.queueable or forced_queue:
            for actor in objlist:
                actor.queue_cmd(self, args) # NOTE: No args unpacking
        else:
            for actor in objlist:
                self.do_instant(session, actor, *args)

    def do_instant(self, session, actor, *args):
        for req in self.instant_reqs:
            req, what = req(session, actor)
            if not req:
                session.tell_required(actor, what)
                return False
        for req in self.delayed_reqs:
            req, what = req(session, actor)
            if not req:
                session.tell_required(actor, what)
                return False
        if self.instant is not None:
            self.instant(session, actor, *args)
        return True

    def do_delayed(self, session, actor, *args):
        if self.delayed is not None:
            self.delayed(session, actor, *args)
        if self.post is not None:
            self.post(session, actor, *args)



class StartedCommand:
    def __init__(self, session, actor, command, *args):
        self.is_placeholder = False
        self.session = session
        self.actor = actor
        self.command = command
        self.args = args
        self.start_tick = self.session.tick

    @classmethod
    def placeholder(cls):
        obj = cls.__new__(cls)
        obj.is_placeholder = True
        return obj

    def check_done(self):
        if self.command.duration != None:
            return self.session.tick >= self.command.duration + self.start_tick
        else:
            return self.command.end(self)

    def do_instant(self):
        self.command.do_instant(self.session, self.actor, *self.args)

    def do_delayed(self):
        self.command.do_delayed(self.session, self.actor, *self.args)
