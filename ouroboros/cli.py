from os import environ
import argparse
import docker
import re
import defaults

api_client = None


def checkURI(uri):
    """Validate tcp:// regex"""
    regex = re.compile(r"""(?xi) # "verbose" mode & case-insensitive
        \A                        # in the beginning...
        tcps?://                  # tcp or tcps protocol
        (?:                       # hostname / IP address
         (?:                      # short or FQDN
          (?![-.a-z0-9]{254,})    # up to 253 total chars in identifier
          (?![.0-9]+)             # not completely numeric
          (?:                     # hostname part
           (?=[a-z0-9])           # starts with alnum only
           [-a-z0-9]{1,63}        # 1-63 alphanumeric or hyphen chars
           (?<=[a-z0-9])          # ends with alnum only
          )
          (?:                     # domain name components are less strict
           \.                     # period separator
           [-a-z0-9]{1,63}        # 1-63 alphanumeric or hyphen chars
           (?<!-)                 # doesn't end with a hyphen
          )*                      # zero or more domain components
         )|(?:                    # or an IP address
          (?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}  # 0-255
             (?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)
         )
        )
        (?::\d{1,5})?             # optional port
        (?:/\S*)?                 # optional path / trailing slash
        \Z
        """)
    return re.match(regex, uri)


def get_int_env_var(env_var):
    """Attempt to convert environment variable to int"""
    try:
        return int(env_var)
    except (ValueError, TypeError):
        return False


def parse(sysargs):
    """Declare command line options"""
    global api_client
    parser = argparse.ArgumentParser(description='ouroboros',
                                     epilog='Example: python3 main.py -u tcp://1.2.3.4:5678 -i 20 -m container1 container2 -l warn')

    parser.add_argument('-u', '--url', default=defaults.LOCAL_UNIX_SOCKET,
                        help='Url for tcp host (defaults to "unix://var/run/docker.sock")')

    parser.add_argument('-i', '--interval', type=int, default=get_int_env_var(env_var=environ.get('INTERVAL')) or defaults.INTERVAL, dest='interval',
                        help='Interval in seconds between checking for updates (defaults to 300s)')

    parser.add_argument('-m', '--monitor', nargs='+', default=environ.get('MONITOR') or [], dest='monitor',
                        help='Which container to monitor (defaults to all running).')

    parser.add_argument('-l', '--loglevel', choices=['notset', 'debug', 'info', 'warn', 'error', 'critical'],
                        dest="loglevel", default=environ.get('LOGLEVEL') or 'info',
                        help='Change logger mode (defaults to info)')

    parser.add_argument('-r', '--runonce', default=environ.get('RUNONCE') or False, dest='run_once',
                        help='Only run ouroboros once then exit', action='store_true')

    parser.add_argument('-c', '--cleanup', default=environ.get('CLEANUP') or False, dest='cleanup',
                        help='Remove old images after updating', action='store_true')

    parser.add_argument('--metrics', type=int, default=get_int_env_var(env_var=environ.get('METRICS')) or defaults.METRICS_PORT, dest='metrics',
                        help='Enable prometheus endpoint')
    args = parser.parse_args(sysargs)

    if not args.url:
        args.url = defaults.LOCAL_UNIX_SOCKET
    else:
        if args.url is not defaults.LOCAL_UNIX_SOCKET:
            args.url = args.url if checkURI(
                args.url) else defaults.LOCAL_UNIX_SOCKET

    api_client = docker.APIClient(base_url=args.url)
    return args
