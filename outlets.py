#!/bin/env python

import subprocess
import argparse
import json
import os

class OutletSuite(object):
    def __init__(self,config_block):
        self.config_block = config_block

    def turn(self,name,state):
        if name in self.config_block["outlets"]:
            this_outlet = self.config_block["outlets"][name]
            subprocess.call([self.config_block["code_sender"],
                this_outlet[state]
                ])

    def on(self,name):
        self.turn(name,"on")
        
    def off(self,name):
        self.turn(name,"off")

    def list(self):
        return self.config_block["outlets"].keys()

def cli_parser():
    parser = argparse.ArgumentParser(description='Manage Etekcity Outlets')
    parser.add_argument('--list', action='store_true', help='List the available outlets')
    parser.add_argument('-c','--config',required=True,help="Configuration file to load")
    parser.add_argument('--on', action='store_true',help='Turn the specified outlet on')
    parser.add_argument('--off', action='store_true',help='Turn the specified outlet off')
    parser.add_argument('outlet',nargs='?', help='The name of the outlet to control')

    return parser

def main():
    parser = cli_parser()
    args = parser.parse_args()

    if not os.path.exists(args.config):
        print("You must specify an existing configuration file")
        exit(1)

    config = json.load(open(args.config))
    suite = OutletSuite(config['outlet_config'])

    if args.list:
        print(suite.list())
    else:
        if args.outlet is None:
            print("You must specify an outlet")
            exit(1)
        elif not args.outlet in suite.list():
            print "Unrecognized outlet.  Choose from this list: %r"%(suite.list())
        else:
            if args.on:
                suite.on(args.outlet)
            if args.off:
                suite.off(args.outlet)

if __name__ == "__main__":
    main()
