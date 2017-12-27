#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# just for test
from __future__ import print_function

import argparse
import json
import os
import socket
import sys
from xcatagent import utils

class ClientShell(object):
    def get_base_parser(self):
        parser = argparse.ArgumentParser(
            prog='agentclient',
            add_help=False,
            formatter_class=HelpFormatter,
        )
        parser.add_argument('-h', '--help',
                            action='store_true',
                            help=argparse.SUPPRESS,
                            )
        parser.add_argument('--sock',
                            help="The unix domain sock file to communicate "
                                 "with the server",
                            default='/var/run/xcat/agent.sock',
                            type=str)
        return parser

    def do_help(self, args):
        self.parser.print_help()

    def main(self, argv):
        self.parser = self.get_base_parser()
        (options, args) = self.parser.parse_known_args(argv)

        if options.help:
            self.do_help(options)
            return 0

        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        nodes = ['node%s' % i for i in range(100)]
        nodeinfo = {node: {'username': 'admin', 'password': 'cluster'} for node
                    in
                    nodes}

        s.connect(options.sock)
        req = {'module': 'openbmc',
               'command': 'rpower',
               'args': ['-d', 'firmware'],
               'cwd': os.getcwd(),
               'nodes': nodes,
               'nodeinfo': nodeinfo}

        buf = json.dumps(req)
        s.send(utils.int2bytes(len(buf)))
        s.send(buf)
        while True:
            sz = s.recv(4)
            if len(sz) == 0:
                break
            sz = utils.bytes2int(sz)
            data = s.recv(sz)
            print(data)


class HelpFormatter(argparse.HelpFormatter):
    def start_section(self, heading):
        # Title-case the headings
        heading = '%s%s' % (heading[0].upper(), heading[1:])
        super(HelpFormatter, self).start_section(heading)


if __name__ == '__main__':
    ClientShell().main(sys.argv[1:])