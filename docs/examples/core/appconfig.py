"""A simple example of how to use IPython.config.application.Application.

This should serve as a simple example that shows how the IPython config
system works. The main classes are:

* IPython.config.configurable.Configurable
* IPython.config.configurable.SingletonConfigurable
* IPython.config.loader.Config
* IPython.config.application.Application

To see the command line option help, run this program from the command line::

    $ python appconfig.py -h

To make one of your classes configurable (from the command line and config
files) inherit from Configurable and declare class attributes as traits (see
classes Foo and Bar below). To make the traits configurable, you will need
to set the following options:

* ``config``: set to ``True`` to make the attribute configurable.
* ``shortname``: by default, configurable attributes are set using the syntax
  "Classname.attributename". At the command line, this is a bit verbose, so
  we allow "shortnames" to be declared. Setting a shortname is optional, but
  when you do this, you can set the option at the command line using the
  syntax: "shortname=value".
* ``help``: set the help string to display a help message when the ``-h``
  option is given at the command line. The help string should be valid ReST.

When the config attribute of an Application is updated, it will fire all of
the trait's events for all of the config=True attributes.
"""

import sys

from IPython.config.configurable import Configurable
from IPython.config.application import Application
from IPython.utils.traitlets import (
    Bool, Unicode, Int, Float, List, Dict
)


class Foo(Configurable):
    """A class that has configurable, typed attributes.

    """

    i = Int(0, config=True, help="The integer i.")
    j = Int(1, config=True, help="The integer j.")
    name = Unicode('Brian', config=True, help="First name.")


class Bar(Configurable):

    enabled = Bool(True, config=True, help="Enable bar.")


class MyApp(Application):

    app_name = Unicode('myapp')
    running = Bool(False, config=True,
                   help="Is the app running?")
    classes = List([Bar, Foo])
    config_file = Unicode('', config=True,
                   help="Load this config file")
    
    aliases = Dict(dict(i='Foo.i',j='Foo.j',name='Foo.name', running='MyApp.running',
                        enabled='Bar.enabled', log_level='MyApp.log_level'))
    
    flags = Dict(dict(enable=({'Bar': {'enabled' : True}}, "Enable Bar"),
                  disable=({'Bar': {'enabled' : False}}, "Disable Bar"),
                  debug=({'MyApp':{'log_level':10}}, "Set loglevel to DEBUG")
            ))
    
    def init_foo(self):
        # Pass config to other classes for them to inherit the config.
        self.foo = Foo(config=self.config)

    def init_bar(self):
        # Pass config to other classes for them to inherit the config.
        self.bar = Bar(config=self.config)



def main():
    app = MyApp()
    app.parse_command_line()
    if app.config_file:
        app.load_config_file(app.config_file)
    app.init_foo()
    app.init_bar()
    print("app.config:")
    print(app.config)


if __name__ == "__main__":
    main()
