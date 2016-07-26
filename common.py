#!/usr/bin/env python3
"""Common utility functions."""

from logging.handlers import SysLogHandler

import sys
import logging
import socket


def setup_logging(logger, syslog_socket, log_format):
    """Configure logging."""
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(log_format)

    consoleHandler = logging.StreamHandler(sys.stdout)
    consoleHandler.setFormatter(formatter)
    logger.addHandler(consoleHandler)
    logger.propagate = False

    if syslog_socket != '/dev/null':
        syslogHandler = SysLogHandler(syslog_socket)
        syslogHandler.setFormatter(formatter)
        logger.addHandler(syslogHandler)


def set_marathon_auth_args(parser):
    """Set the authorization for Marathon."""
    parser.add_argument("--marathon-auth-credential-file",
                        help="Path to file containing a user/pass for "
                        "the Marathon HTTP API in the format of 'user:pass'."
                        )

    return parser


def get_marathon_auth_params(args):
    """Get the Marathon credentials from a file."""
    if args.marathon_auth_credential_file is None:
        return None

    line = None
    with open(args.marathon_auth_credential_file, 'r') as f:
        line = f.readline().rstrip('\r\n')

    if line is not None:
        splat = line.split(':')
        return (splat[0], splat[1])

    return None


def set_logging_args(parser):
    """Add logging-related args to the parser."""
    default_log_socket = "/dev/log"
    if sys.platform == "darwin":
        default_log_socket = "/var/run/syslog"

    parser.add_argument("--syslog-socket",
                        help="Socket to write syslog messages to. "
                        "Use '/dev/null' to disable logging to syslog",
                        default=default_log_socket
                        )
    parser.add_argument("--log-format",
                        help="Set log message format",
                        default="%(asctime)s %(name)s: %(levelname)"
                        " -8s: %(message)s"
                        )
    return parser


def unique(l):
    """Return the unique elements of a list."""
    return list(set(l))


def list_diff(list1, list2):
    """Return the difference between two lists."""
    return list(set(list1) - set(list2))


def list_intersect(list1, list2):
    """Return the intersection of two lists."""
    return list(set.intersection(set(list1), set(list2)))


ip_cache = dict()


def resolve_ip(host):
    """Get the IP address for a hostname."""
    cached_ip = ip_cache.get(host, None)
    if cached_ip:
        return cached_ip
    else:
        try:
            ip = socket.gethostbyname(host)
            ip_cache[host] = ip
            return ip
        except socket.gaierror:
            return None
