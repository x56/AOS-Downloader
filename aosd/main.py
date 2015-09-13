import sys
import argparse
import readline
import rlcompleter

from .commandparse import *
from .downloader import *

def GetPassedCommandArgs(args):
    kValidCommands = [
        'list',
        'fetch',
        'diff',
        'setup_cache',
        'reset_cache',
        'build_cache'
    ];
    # returns the list of recognized commands passed as args
    return list((cmd for cmd in args if cmd in kValidCommands and args[cmd] == True));

def GetPassedFilterArgs(args):
    kValidFilters = [
        'type',
        'version',
        'package',
        'build'
    ];
    # returns the list of recognized filters passed as args
    return list((filt for filt in args if filt in kValidFilters and args[filt] != None));

def CheckPassedCommandArgCount(args):
    return len(GetPassedCommandArgs(args))

def CheckPassedFilterArgCount(args):
    return len(GetPassedFilterArgs(args))

def DisplayUnusedFilterArgs(args, unused):
    for ignored in set(GetPassedFilterArgs(args)) & set(unused):
        logging_helper.getLogger().info(': Ignoring %s filter "%s"' % (ignored, args[ignored]));

def main():
    parser = argparse.ArgumentParser(description='Apple Open Source Package Downloader');
    command_group = parser.add_argument_group('command arguments')
    command_group.add_argument(
        '-l',
        '--list',
        help='list available builds of a package, if no package is specified then list available packages',
        action='store_true'
    );
    
    command_group.add_argument(
        '-f',
        '--fetch',
        help='download all available packages, optionally filtering by type, version, package, and/or build',
        action='store_true'
    );
    
    command_group.add_argument(
        '-d',
        '--diff',
        help='generate diff between specified versions of a package',
        action='store_true'
    );
    
    command_group.add_argument(
        '-s',
        '--setup-cache',
        help='fully clean, fetch, and rebuild package manifests and index',
        action='store_true'
    );
    
    command_group.add_argument(
        '-r',
        '--reset_cache',
        help='remove cached package manifests, optionally filtering by type and/or version, and rebuild index',
        action='store_true'
    );
    
    command_group.add_argument(
        '-c',
        '--build-cache',
        help='cache the package manifests, optionally filtering by type and/or version, and rebuild index',
        action='store_true'
    );
    
    filter_group = parser.add_argument_group('filter arguments');
    filter_group.add_argument(
        '-t',
        '--type',
        help='specify the release type',
        required=False,
        action='store'
    );
    
    filter_group.add_argument(
        '-v',
        '--version',
        help='specify the version number from a release type',
        required=False,
        action='store'
    );
    
    filter_group.add_argument(
        '-p',
        '--package',
        help='specify the name of a package from a release',
        required=False,
        action='store'
    );
    
    filter_group.add_argument(
        '-b',
        '--build',
        help='specify the build number of a package',
        required=False,
        action='store'
    );
    
    args_dict = vars(parser.parse_args());
    
    if config.getFirstRun() == True:
        logging_helper.getLogger().info(': This appears to be the first time this has been run, it is highly recommended that you run the "cache setup" command or pass "--setup-cache" on the command line. This software can be used without this command being run but some of the autocomplete will not work.');
    
    if CheckPassedCommandArgCount(args_dict) == 0:
        if CheckPassedFilterArgCount(args_dict) != 0:
            logging_helper.getLogger().info(': Ignoring filters; initializng interpreter filters via command line flags not currently implemented.');
        
        if 'libedit' in readline.__doc__:
            readline.parse_and_bind("bind ^I rl_complete");
        else:
            readline.parse_and_bind("tab: complete");
        aosd_shell = input();
        aosd_shell.cmdloop();
    else:
        if CheckPassedCommandArgCount(args_dict) == 1:
            command = GetPassedCommandArgs(args_dict)[0];
            
            release_type = args_dict['type']
            release_version = args_dict['version']
            package_name = args_dict['package']
            build_number = args_dict['build']
                        
            if command == 'list':
                DisplayUnusedFilterArgs(args_dict, ('type', 'version'));
            
            if command == 'fetch':
                pass
            
            if command == 'diff':
                pass
            
            if command == 'setup_cache':
                DisplayUnusedFilterArgs(args_dict, ('type', 'version', 'package', 'build'));
                cacher.flush(None, None);
                cacher.fetch(None, None);
                cacher.rebuild()
            
            if command == 'reset_cache':
                DisplayUnusedFilterArgs(args_dict, ('package', 'build'));
                cacher.flush(release_type, release_version);
                cacher.rebuild()
            
            if command == 'build_cache':
                DisplayUnusedFilterArgs(args_dict, ('package', 'build'));
                cacher.fetch(release_type, release_version);
                cacher.rebuild()
            
        else:
            logging_helper.getLogger().error(': Multiple command flags specified, please choose only one.');

if __name__ == "__main__":
    main();