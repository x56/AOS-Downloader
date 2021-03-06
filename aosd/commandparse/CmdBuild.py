"""
imports
"""
from .RootCmd import RootCmd
from ..downloader.Builds import Builds

class CmdBuild(RootCmd):
    """
    command to select a build number of a package
    """

    @classmethod
    def usage(cls):
        """
        command usage information
        """
        return {
            'name': 'build',
            'args': '<build version>',
            'desc': 'selects a build version for the currently selected package'
        }

    @classmethod
    def valid_values(cls, release_type, package_name):
        """
        fetches the builds for a specific package
        """
        return Builds.get(release_type, package_name)

    @classmethod
    def query(cls, release_type, package_name, args):
        """
        validate the value passed to the command
        """
        # only use the first value
        if len(args) > 0:
            return (args[0] in cls.valid_values(release_type, package_name), args[0])
        else:
            return (False, None)
