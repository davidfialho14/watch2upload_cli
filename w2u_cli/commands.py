from docopt import docopt
from prettytable import PrettyTable

from w2u_cli.watch2upload import Watch2Upload


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
