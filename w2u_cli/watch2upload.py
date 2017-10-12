import os
from collections import namedtuple
from urllib.parse import urlparse

from recordclass import recordclass

Watch = recordclass("Watch", "directory remote_url remote_username "
                             "remote_dir enable delete")

Remote = namedtuple("Remote", "id url username")


class RemoteNotFoundError(Exception):
    """ Raised when a remote is not found """


class RemoteExistsError(Exception):
    """ Raised trying to add a remote that already exists """


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

        # Raise error if watch already exists
        if self._find_watch(directory):
            raise DirectoryExistsError("directory `%s` is already being "
                                       "watched" % directory)

        self._watches.append(Watch(
            os.path.abspath(directory),
            remote_url,
            remote_username,
            remote_dir,
            enable,
            delete
        ))

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
        watch = self._find_watch(directory)
        self._watches.remove(watch)

    def enable_watch(self, directory):
        watch = self._find_watch(directory)
        watch.enable = True

    def disable_watch(self, directory):
        watch = self._find_watch(directory)
        watch.enable = False

    def set_watch_conf(self, directory, config, value):
        """
        Sets a value for the configuration identified by the specified
        key/label.

        :param directory: watched directory to configure
        :param config:    key for the configuration to set value for
        :param value:     value to set for the configuration
        :raise KeyError:   if the specified config key was not recognized
        :raise ValueError: if the specified value is invalid for the
                           specified configuration
        :raise DirectoryNotFoundError: if *directory* is not included in the
                                       watch list
        """
        watch = self._find_watch(directory)

        if config == 'remote-dir':
            watch.remote_dir = value

        elif config == 'remote-url':
            watch.remote_url = value

        elif config == 'remote-username':
            watch.remote_username = value

        elif config == 'remote-password':
            # This will change in the actual application
            pass

        elif config == 'delete':
            if value == "1":
                watch.delete = True
            elif value == "0":
                watch.delete = False
            else:
                raise ValueError("unexpected value `%s`" % value)

        else:
            raise KeyError("unrecognized configuration key")

    def get_watch_conf(self, directory, config):
        """
        Gets the value for the configuration identified by the specified
        key/label.

        :param directory: watched directory to get value for
        :param config:    key for the configuration to get value for
        :raise KeyError:   if the specified config key was not recognized
        :raise DirectoryNotFoundError: if *directory* is not included in the
                                       watch list
        """
        watch = self._find_watch(directory)

        if config == 'remote-dir':
            return watch.remote_dir

        elif config == 'remote-url':
            return watch.remote_url

        elif config == 'remote-username':
            return watch.remote_username

        elif config == 'delete':
            return "1" if watch.delete else "0"

        else:
            raise KeyError("unrecognized key")

    def add_remote(self, url, username, password):

        self._validate_url(url)

        # Check if remote already exists
        for remote in self._remotes.values():
            if remote == (url, username):
                raise RemoteExistsError()

    def remotes(self) -> list:
        return [Remote(id, remote[0], remote[1])
                for id, remote in self._remotes.items()]

    def remove_remote(self, remote_id):
        try:
            del self._remotes[remote_id]
        except KeyError:
            raise RemoteNotFoundError()

    def get_remote_conf(self, remote_id, config):

        if config == "url":
            return self._remotes[remote_id][0]
        elif config == "username":
            return self._remotes[remote_id][1]
        else:
            raise KeyError("unrecognized configuration key")

    def _find_watch(self, directory):
        full_directory = os.path.abspath(directory)
        for watch in self._watches:
            if watch.directory == full_directory:
                return watch

        # Did not find watch: raise error
        raise DirectoryNotFoundError(
            "directory `%s` not found in watch list" % directory)

    def _validate_url(self, url: str):
        """
        Validates an url in string format. It checks if the URL scheme is
        actually http/https.

        Raises a ValueError if the URL is not a valid HTTP url.
        """
        result = urlparse(url)

        if result.scheme not in ('http', 'https') \
                or not result.netloc or not result.path:
            raise ValueError("URL is not valid: %s" % url)
