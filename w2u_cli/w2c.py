"""
Watch2Upload CLI

Usage:
  w2u <command>
  w2u (-h | --help)
  w2u --version

Options:
  -h --help   Show this screen.
  --version   Show version.

Commands:
  add      Adds a new directory
  list     Lists watched directories
  remove   Removes a directory
  enable   Enables watching a directory
  disable  Disables watching a directory
  set      Changes a configuration option
  get      Prints a configuration option
  remote   Manages remote servers
"""
import sys
from docopt import docopt

import w2u_cli.commands as cmds
from w2u_cli.watch2upload import Watch2Upload


commands = {
    'add': cmds.add,
    'list': cmds.list,
}


def main():

    # Here we want to parse only the first input argument (the command) and
    # allow any other arguments following the first.
    # Since it is only one argument, the use of docopt maybe overkill
    #
    # Two reasons to support the use of docopt here:
    #   - keep consistency in error message. For instance, when there are no
    #     arguments the error message includes only the usage and not all the
    #     help message
    #   - makes it easier to make changes. If in the future one or two
    #     arguments are support, or even some options other than hel and
    #     version, docopt will handle that very easily without much change to
    #     the code.
    #
    argv = sys.argv[1] if len(sys.argv) > 1 else []
    args = docopt(__doc__, argv, version="Watch2Upload CLI v0.1")
    command_name = args['<command>']

    try:
        command = commands[command_name]
    except KeyError:
        print("Command '%s' was not recognized, see \"w2c --help\"" %
              command_name, file=sys.stderr)
        sys.exit(1)

    watch2upload = Watch2Upload()
    command(watch2upload)


if __name__ == '__main__':
    main()
