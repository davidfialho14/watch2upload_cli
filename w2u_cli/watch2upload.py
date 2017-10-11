from collections import namedtuple

Watch = namedtuple("Watch", "directory remote_url remote_username "
                            "remote_dir enable delete")


class Watch2Upload:
    """
    Abstraction to access the Watch2Upload service.

    !!! Important !!!
    Right now, this is a fake implementation to test the interface
    """

    _watches = [
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

    def watches(self, enabled=None) -> list:
        if enabled is None:
            return self._watches
        else:
            return [watch for watch in self._watches if watch.enable is enabled]

