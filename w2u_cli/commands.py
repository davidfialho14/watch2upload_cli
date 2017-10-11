import sys

from docopt import docopt
from prettytable import PrettyTable

from w2u_cli.watch2upload import Watch2Upload, RemoteNotFoundError, \
    DirectoryExistsError, DirectoryNotFoundError


def add(watch2upload: Watch2Upload):
    """
The add command adds the specified directory to the list of watched directories.

See "list" command to look at all directories being watched.
The added directory is enabled by default, see "enable" and "disable" commands.

Usage:
  w2u add <directory> <remote_id> <remote_dir> [--delete]

Options:
  --delete  Delete files once they are uploaded to the remote server
"""
    args = docopt(str(add.__doc__))

    directory = args['<directory>']
    remote_id = args['<remote_id>']
    remote_dir = args['<remote_dir>']
    delete_option = args['--delete']

    try:
        watch2upload.add_watch(directory, remote_id, remote_dir, delete_option)

    except ValueError as error:
        print("error:", str(error), file=sys.stderr)
        sys.exit(1)

    except RemoteNotFoundError as error:
        print("error:", str(error), file=sys.stderr)
        print("  type \"w2u remote list\" to see all remotes")
        sys.exit(1)

    except DirectoryExistsError as error:
        print("error:", str(error), file=sys.stderr)
        print("  type \"w2u list --all\" to see all watches")
        print("  type \"w2u get remote %s\" to see the remote associated with "
              "the directory" % directory)
        sys.exit(1)


def list(watch2upload: Watch2Upload):
    """
The list command lists the directories being watched by Watch2Upload.

Usage:
  w2u list [options]

Options:
  -a --all  Show all watched directories, including disabled directories
"""
    args = docopt(str(list.__doc__))
    list_all = args['--all']

    table = PrettyTable((
        "Directory",
        "Enabled",
        "Remote Directory",
        "URL",
        "Username",
        "Delete Option"
    ))

    # Align the following columns to the left
    table.align["Directory"] = "l"
    table.align["Remote Directory"] = "l"
    table.align["URL"] = "l"
    table.align["Username"] = "l"

    # Decide whether to list all watched directories or only those enabled
    list_only_enabled = None if list_all else True

    for watch in watch2upload.watches(list_only_enabled):
        table.add_row((
            watch.directory,
            _check_mark(watch.enable),
            watch.remote_dir,
            watch.remote_url,
            watch.remote_username,
            _check_mark(watch.delete),
        ))

    print(table)


def remove(watch2upload: Watch2Upload):
    """
The remove command removes the specified directories from the watched
directories list.

See "list" command to look at all directories being watched.

Usage:
  w2u remove <directory>
"""
    args = docopt(str(remove.__doc__))
    directory = args['<directory>']

    try:
        watch2upload.remove_watch(directory)

    except DirectoryNotFoundError as error:
        print("warning:", str(error), file=sys.stderr)
        print("  type \"w2u list --all\" to see all watches")
        sys.exit(1)


def enable(watch2upload: Watch2Upload):
    """
The enable command enables actively watching a directory that is not actively
watched.

Usage:
  w2u enable <directory>
"""
    args = docopt(str(enable.__doc__))
    directory = args['<directory>']

    try:
        watch2upload.enable_watch(directory)

    except DirectoryNotFoundError as error:
        print("error:", str(error), file=sys.stderr)
        print("  type \"w2u list --all\" to see all watches")
        sys.exit(1)


def disable(watch2upload: Watch2Upload):
    """
The disable command disables watching a directory that is being actively
watched.

Usage:
  w2u disable <directory>
"""
    args = docopt(str(disable.__doc__))
    directory = args['<directory>']

    try:
        watch2upload.disable_watch(directory)

    except DirectoryNotFoundError as error:
        print("error:", str(error), file=sys.stderr)
        print("  type \"w2u list --all\" to see all watches")
        sys.exit(1)


def set(watch2upload: Watch2Upload):
    """
The set command changes the value of the specified configuration.

Usage:
  w2u set <config> <value> <directory>

Arguments:
  <config>     Configuration key name
  <value>      Value to set for the configuration
  <directory>  Directory (in watch list) to set configuration for

Config keys:
  remote-dir       Remote directory where to upload directory's data
  remote-url       URL of the remote server where to upload data
  remote-username  Username to login to the server
  remote-password  Password to login to the server
  delete           Enable/disable deleting files after they are uploaded
                   (enable=1 and disable=0)
"""
    args = docopt(str(set.__doc__))
    config = args['<config>']
    value = args['<value>']
    directory = args['<directory>']

    try:
        watch2upload.set_conf(directory, config, value)

    except DirectoryNotFoundError as error:
        print("error:", str(error), file=sys.stderr)
        print("  type \"w2u list --all\" to see all watches")
        sys.exit(1)

    except KeyError:
        print("error: configuration key `%s` unknown" % config, file=sys.stderr)
        print("  type \"w2u set --help\" to see all configuration keys "
              "available", file=sys.stderr)
        sys.exit(1)

    except ValueError as error:
        print("error:", str(error), file=sys.stderr)
        print("  type \"w2u set --help\" for help", file=sys.stderr)
        sys.exit(1)


def _check_mark(option: bool):
    return "✔" if option else "x"
