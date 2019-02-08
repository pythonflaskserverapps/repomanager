###################################################

import argparse
import subprocess
from pathlib import Path
from github import Github

###################################################

from utils import create_dir, read_string_from_file, write_string_to_file, read_json_from_file, rmtree

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

def repoconfigpath(name = None):
    if not name:
        name = reponame
    return repopath("{}.json".format(name))

def creategitconfig(gituser, gitmail, reponame):
    template = read_string_from_file("configtemplate", "")
    template = template.replace("${gituser}", gituser)
    template = template.replace("${gitmail}", gitmail)
    template = template.replace("${reponame}", reponame)
    return template

def readrepoconfigjson(name = None):    
    return read_json_from_file(repoconfigpath(name), {})

###################################################

create_dir("repos")

parser = argparse.ArgumentParser(description='Manage repos')

parser.add_argument('-c', '--create', help='create repo')
parser.add_argument('-p', '--populate', help='create repo')
parser.add_argument('--force', action = "store_true", help='force')

args = parser.parse_args()

###################################################

print(args)

if args.create:    
    reponame = args.create
    print("creating {} as {}".format(reponame, repopath()))
    if args.force:
        rmtree(repopath())
    create_dir(repopath())
    write_string_to_file(repoconfigpath(), read_string_from_file("repotemplate.json", "{}"), force = args.force)    

if args.populate:
    reponame = args.populate
    if args.force:
        print("removing .git")
        rmtree(repofilepath(".git"))
    subprocess.Popen(["git", "init"], cwd = Path(repopath())).wait()
    configjson = readrepoconfigjson()        
    gituser = configjson["gituser"]
    gitpass = configjson["gitpass"]
    gitmail = configjson["gitmail"]
    gitconfig = creategitconfig(gituser, gitmail, reponame)
    write_string_to_file(repofilepath(".git/config"), gitconfig)
    print("written gitconfig")
    write_string_to_file(repofilepath(".gitignore"), read_string_from_file("gitignoretemplate", ""), force = args.force)    
    print("written .gitignore")
    g = Github(gituser, gitpass)
    u = g.get_user()
    if args.force:
        try:
            u.get_repo(reponame).delete()
            print("deleted github repo")
        except:
            print("github repo does not exist")
    try:
        u.create_repo(reponame)
        print("created github repo")
    except:
        print("github repo already exists")
    if args.force:        
        subprocess.Popen(["git", "add", "."], cwd = Path(repopath())).wait()
        subprocess.Popen(["git", "commit", "-m", "Initial commit"], cwd = Path(repopath())).wait()
        subprocess.Popen(["git", "push", "github", "master"], cwd = Path(repopath())).wait()