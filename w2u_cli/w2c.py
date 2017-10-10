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
from docopt import docopt


def main():
    args = docopt(__doc__)
    print(args)


if __name__ == '__main__':
    main()
