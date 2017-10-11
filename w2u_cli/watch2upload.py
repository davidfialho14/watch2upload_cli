import os
from collections import namedtuple

Watch = namedtuple("Watch", "directory remote_url remote_username "
                            "remote_dir enable delete")

Remote = namedtuple("Remote", "id url username")


class RemoteNotFoundError(Exception):
    """ Raised when a remote is not found """


class DirectoryNotFoundError(Exception):
    """ Raised when a directory is not found in the watch list """


class DirectoryExistsError(Exception):
    """ Raised trying to add a directory that already exists """


class Watch2Upload:
    """
    Abstraction to access the Watch2Upload service.

    !!! Important !!!
    Right now, this is a fake implementation to test the interface
    """

    def __init__(self):
        self._watches = [
            Watch(
                directory="/local/dir",
                remote_url="http://server.com",
                remote_username="user",
                remote_dir="/remote/dir",
                enable=True,
                delete=False
            ),
            Watch(
                directory="/local/example",
                remote_url="http://server.com",
                remote_username="user",
                remote_dir="/remote/example",
                enable=True,
                delete=True
            ),
            Watch(
                directory="/local/somedir",
                remote_url="http://someserver.com",
                remote_username="user1",
                remote_dir="/remote/somedir",
                enable=False,
                delete=False
            )
        ]

        self._remotes = {
            "#1": ("http://server.com", "user"),
            "#2": ("http://someserver.com", "user1"),
        }

    def add_watch(self, directory, remote_id, remote_dir, delete, enable=True):
        """
        Adds a new directory to the watch list.

        :param directory:  path for directory to watch
        :param remote_id:  ID of the remote to upload directory contents to
        :param remote_dir: directory in the remote server to upload directory
                           contents to
        :param delete:     set to True to enable deleting contents once they
                           are uploaded
        :param enable:     set to True to enable this watch or false to disable
        :raise RemoteNotFoundError:  if a remote with the specified ID is not
                                     available in the remotes list
        :raise DirectoryExistsError: if the specified directory is already
                                     included in the watch list
        :raise ValueError:           if some of the specified parameters is not
                                     is not valid
        """
        if not os.path.isdir(directory):
            raise ValueError("directory `%s` does not exist" % directory)

        try:
            remote_url, remote_username = self._remotes[remote_id]
        except KeyError:
            raise RemoteNotFoundError("remote with id=%s not found" % remote_id)

        full_directory = os.path.abspath(directory)

        # Check if the watch already exists
        for watch in self._watches:
            if watch.directory == full_directory:
                raise DirectoryExistsError("directory `%s` is already being "
                                           "watched" % directory)

        self._watches.append(Watch(full_directory, remote_url, remote_username,
                                   remote_dir, enable, delete))

    def watches(self, enabled=None) -> list:
        """ Returns a list with all the watches in the watch list """
        if enabled is None:
            return self._watches
        else:
            return [watch for watch in self._watches if watch.enable is enabled]

    def remove_watch(self, directory):
        """

        :param directory:
        :raise DirectoryNotFoundError: if the specified directory is not
                                       found in the watch list
        """
        full_directory = os.path.abspath(directory)

        watch_to_remove = None
        for watch in self._watches:
            if watch.directory == full_directory:
                watch_to_remove = watch

        if watch_to_remove is None:
            raise DirectoryNotFoundError("directory `%s` not found in watch "
                                         "list" % directory)

        self._watches.remove(watch_to_remove)
