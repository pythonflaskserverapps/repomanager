###################################################

import argparse

###################################################

from utils import create_dir, read_string_from_file, write_string_to_file

###################################################

REPOS_ROOT = "repos"

###################################################

reponame = None

###################################################

def filepath(path):
    return "{}/{}".format(REPOS_ROOT, path)

def repopath(name = None):
    global reponame
    if not name:
        name = reponame
    return filepath(name)

def repofilepath(path):
    return "{}/{}".format(repopath(), path)

def repojsonpath(name = None):
    if not name:
        name = reponame
    return repofilepath("{}.json".format(name))

###################################################

create_dir("repos")

parser = argparse.ArgumentParser(description='Manage repos')

parser.add_argument('-c', '--create', help='create repo')

args = parser.parse_args()

###################################################

print(args)

if args.create:    
    reponame = args.create
    print("creating {} as {}".format(reponame, repopath()))
    create_dir(repopath())
    write_string_to_file(repojsonpath(), read_string_from_file("repotemplate.json", "{}"))