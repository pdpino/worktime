#!/usr/bin/env python
"""Push or pull the worktime git repository """

import subprocess
import argparse
import sys


def run(cmd):
	print("calling: {}".format(cmd))
	ret = subprocess.run(cmd, shell=True)
	if ret.returncode > 0: # subprocess had an error, exiting
		print("There whas an error, code: {}".format(ret.returncode))
		sys.exit(ret.returncode)



# Parse options
parser = argparse.ArgumentParser(description='Push or pull the worktime repository', usage='%(prog)s [options]')

subparser = parser.add_subparsers(dest='action')

# Push
parser_push = subparser.add_parser('push',
                  help="Push your work")
parser_push.add_argument('--msg', default="add job entries", type=str,
                  help="Message to the commit")

# Pull
parser_pull = subparser.add_parser('pull',
                  help="Pull your work from the repo")

args = parser.parse_args()



# directorio de este proyecto
root_path = sys.path[0] + "/"

cmd = "cd {}; pwd;".format(root_path)

if args.action == "push":
	cmd += " git add .;"
	cmd += " git commit -m '{}';".format(args.msg)
	cmd += " git push;"	
elif args.action == "pull":
	cmd += " git pull;"

run(cmd)


