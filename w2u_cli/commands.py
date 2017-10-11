import sys

from docopt import docopt
from prettytable import PrettyTable

from w2u_cli.watch2upload import Watch2Upload, RemoteNotFoundError, \
    DirectoryExistsError


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


def _check_mark(option: bool):
    return "✔" if option else "x"
