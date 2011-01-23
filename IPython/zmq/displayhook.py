import builtins

from .session import extract_header

class DisplayHook(object):

    def __init__(self, session, pub_socket):
        self.session = session
        self.pub_socket = pub_socket
        self.parent_header = {}

    def __call__(self, obj):
        if obj is None:
            return

        builtins._ = obj
        msg = self.session.send(self.pub_socket, 'pyout', {'data':repr(obj)},
                               parent=self.parent_header)

    def set_parent(self, parent):
        self.parent_header = extract_header(parent)