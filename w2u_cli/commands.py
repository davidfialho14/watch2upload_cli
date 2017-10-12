import sys

from docopt import docopt
from prettytable import PrettyTable

from w2u_cli.watch2upload import Watch2Upload, RemoteNotFoundError, \
    DirectoryExistsError, DirectoryNotFoundError, RemoteExistsError


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
        watch2upload.set_watch_conf(directory, config, value)

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


def get(watch2upload: Watch2Upload):
    """
The get command retrieves the value of the specified configuration.

Usage:
  w2u get <config> <directory>

Arguments:
  <config>     Configuration key name
  <directory>  Directory (in watch list) from which the configuration value is to be read

Config keys:
  remote-dir       Remote directory to where directory's data is uploaded
  remote-url       URL of the remote server to where data is uploaded
  remote-username  Username to login to the server
  delete           Enable/disable deleting files after they are uploaded
                   (enable=1 and disable=0)
"""
    args = docopt(str(get.__doc__))
    config = args['<config>']
    directory = args['<directory>']

    try:
        print(watch2upload.get_watch_conf(directory, config))

    except DirectoryNotFoundError as error:
        print("error:", str(error), file=sys.stderr)
        print("  type \"w2u list --all\" to see all watches")
        sys.exit(1)

    except KeyError:
        print("error: configuration key `%s` unknown" % config, file=sys.stderr)
        print("  type \"w2u get --help\" to see all configuration keys "
              "available", file=sys.stderr)
        sys.exit(1)


def remote(watch2upload: Watch2Upload):
    """
The remote command allows the configuration of remote servers.

Usage:
  w2u remote <command>

Commands:
  add      Adds a new remote server
  list     Lists all remote servers
  remove   Removes a remote server
  get      Prints a configuration option
"""
    argv = sys.argv[1:3] if len(sys.argv) > 2 else []
    args = docopt(str(remote.__doc__), argv)

    commands = {
        'add': remote_add,
        'list': remote_list,
        'remove': remote_remove,
        'get': remote_get,
    }

    command = commands[args['<command>']]
    command(watch2upload)


def remote_add(watch2upload: Watch2Upload):
    """
The remote add command adds a new remote server to the Watch2Upload
application.

Usage:
  w2u remote add <url> <username> <password>

Arguments:
  <url>       URL of the remote server
  <username>  Username used for login
  <password>  Password used for login
"""
    args = docopt(str(remote_add.__doc__))
    url = args['<url>']
    username = args['<username>']
    password = args['<password>']

    try:
        watch2upload.add_remote(url, username, password)

    except RemoteExistsError:
        print("error: remote with the specified URL and username was already "
              "added", file=sys.stderr)
        print("  type \"w2u remote list --all\" to see all remotes")
        sys.exit(1)

    except ValueError as error:
        print("error:", str(error), file=sys.stderr)
        sys.exit(1)


def remote_list(watch2upload: Watch2Upload):
    """
The remote list command lists all remote servers added to Watch2Upload.

Usage:
  w2u remote list
"""
    docopt(str(remote_list.__doc__))

    table = PrettyTable((
        "ID",
        "URL",
        "Username"
    ))

    # Align the following columns to the left
    table.align["ID"] = "l"
    table.align["URL"] = "l"
    table.align["Username"] = "l"

    for remote in watch2upload.remotes():
        table.add_row((
            remote.id,
            remote.url,
            remote.username,
        ))

    print(table)


def remote_remove(watch2upload: Watch2Upload):
    """
The remote remove command removes an existing remote server.

Usage:
  w2u remote remove <remote_id>

Arguments:
  <remote_id>  ID of the remote to remove, see "w2u remote list"
"""
    args = docopt(str(remote_remove.__doc__))
    remote_id = args['<remote_id>']

    try:
        watch2upload.remove_remote(remote_id)

    except RemoteNotFoundError:
        print("warning: there is no remote with ID `%s`" % remote_id,
              file=sys.stderr)
        print("  type \"w2u remote list\" to see all remotes")
        sys.exit(1)


def remote_get(watch2upload: Watch2Upload):
    """
The remote get command retrieves the value of the specified configuration
associated with a remote.

Usage:
  w2u remote get <config> <remote_id>

Arguments:
  <config>     Configuration key name
  <remote_id>  ID of remote associated with the configuration value

Config keys:
  url       URL of the remote server
  username  Username to login to the server
"""
    args = docopt(str(remote_get.__doc__))
    config = args['<config>']
    remote_id = args['<remote_id>']

    try:
        print(watch2upload.get_remote_conf(remote_id, config))

    except RemoteNotFoundError:
        print("warning: there is no remote with ID `%s`" % remote_id,
              file=sys.stderr)
        print("  type \"w2u remote list\" to see all remotes")
        sys.exit(1)

    except KeyError:
        print("error: configuration key `%s` unknown" % config, file=sys.stderr)
        print("  type \"w2u remote get --help\" to see all configuration keys "
              "available", file=sys.stderr)
        sys.exit(1)


def _check_mark(option: bool):
    return "✔" if option else "x"
