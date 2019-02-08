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

def createreadme(title, description):
    template = read_string_from_file("README.md.template", "")
    template = template.replace("${title}", title)
    template = template.replace("${description}", description)
    return template

def creategitignore(reponame):
    template = read_string_from_file("gitignore.template", "")
    template = template.replace("${reponame}", reponame)    
    return template

def createmetayaml(gituser, reponame):
    template = read_string_from_file("meta.yaml.template", "")
    template = template.replace("${gituser}", gituser)
    template = template.replace("${reponame}", reponame)
    return template

def createsetuppy(gituser, gitmail, reponame, projectShortDescription, projectDescription):
    template = read_string_from_file("setup.py.template", "")
    template = template.replace("${gituser}", gituser)
    template = template.replace("${gitmail}", gitmail)
    template = template.replace("${reponame}", reponame)
    template = template.replace("${projectDescription}", projectDescription)
    template = template.replace("${projectShortDescription}", projectShortDescription)
    return template

def createtravistest(reponame):
    template = read_string_from_file("travistest.template", "")    
    template = template.replace("${reponame}", reponame)
    return template

def readrepoconfigjson(name = None):    
    return read_json_from_file(repoconfigpath(name), {})

###################################################

create_dir("repos")

parser = argparse.ArgumentParser(description='Manage repos')

parser.add_argument('--create', help='create repo')
parser.add_argument('--populate', help='populate repo')
parser.add_argument('-c', "--commit", help='create commit')
parser.add_argument("--name", help='commit name')
parser.add_argument('-p', "--push", help='push')
parser.add_argument("--createvenv", help='create virtual env')
parser.add_argument("--installvenv", help='install virtual env')
parser.add_argument("--createdist", help='create dist')
parser.add_argument("--twine", help='twine')
parser.add_argument("--twinever", help='twine latest version')
parser.add_argument("--setup", help='open setup')
parser.add_argument("--code", help='open with vscode')
parser.add_argument("--updatever", help='update version')
parser.add_argument("--ver", help='version')
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
    project = configjson["project"]
    projectTitle = project["title"]
    projectDescription = project["description"]
    projectShortDescription = project["shortDescription"]
    gitconfig = creategitconfig(gituser, gitmail, reponame)
    write_string_to_file(repofilepath(".git/config"), gitconfig)
    print("written gitconfig")
    write_string_to_file(repofilepath(".gitignore"), creategitignore(reponame), force = args.force)    
    print("written .gitignore")
    write_string_to_file(repofilepath("README.md"), createreadme(projectTitle, projectDescription), force = args.force)    
    print("written README.md")
    write_string_to_file(repofilepath("LICENSE"), read_string_from_file("LICENSE.template", ""), force = args.force)    
    print("written LICENSE")
    write_string_to_file(repofilepath("bld.bat"), read_string_from_file("bld.bat.template", ""), force = args.force)    
    write_string_to_file(repofilepath("build.sh"), read_string_from_file("build.sh.template", ""), force = args.force)    
    print("written PyPi build files")
    create_dir(repofilepath(reponame))
    write_string_to_file(repofilepath(reponame + "/__init__.py"), read_string_from_file("initpy.template", ""))
    print("created package dir")
    write_string_to_file(repofilepath("Pipfile"), read_string_from_file("Pipfile.template", ""), force = args.force)    
    write_string_to_file(repofilepath("Pipfile.lock"), read_string_from_file("Pipfile.lock.template", ""), force = args.force)    
    print("written pipfiles")
    write_string_to_file(repofilepath("meta.yaml"), createmetayaml(gituser, reponame), force = args.force)    
    print("written meta.yaml")
    write_string_to_file(repofilepath("setup.py"), createsetuppy(gituser, gitmail, reponame, projectShortDescription, projectDescription), force = args.force)    
    print("written setup.py")
    write_string_to_file(repofilepath("travis_test.py"), createtravistest(reponame), force = args.force)    
    print("written travis test")
    g = Github(gituser, gitpass)
    u = g.get_user()
    if args.force:
        try:
            u.get_repo(reponame).delete()
            print("deleted github repo")
        except:
            print("github repo does not exist")
    try:
        u.create_repo(reponame, description = projectShortDescription)
        print("created github repo")
    except:
        print("github repo already exists")
    if args.force:        
        subprocess.Popen(["git", "add", "."], cwd = Path(repopath())).wait()
        subprocess.Popen(["git", "commit", "-m", "Initial commit"], cwd = Path(repopath())).wait()
        subprocess.Popen(["git", "push", "github", "master"], cwd = Path(repopath())).wait()

if args.commit:
    reponame = args.commit
    commitname = args.name
    subprocess.Popen(["git", "add", "."], cwd = Path(repopath())).wait()
    subprocess.Popen(["git", "commit", "-m", commitname], cwd = Path(repopath())).wait()    

if args.push:
    reponame = args.push        
    subprocess.Popen(["git", "push", "github", "master"], cwd = Path(repopath())).wait()

if args.createvenv:
    reponame = args.createvenv
    configjson = readrepoconfigjson()
    pythonpath = configjson["pythonpath"]
    subprocess.Popen(["pipenv", "--python", str(Path(pythonpath))], cwd = Path(repopath())).wait()    

if args.installvenv:
    reponame = args.installvenv    
    subprocess.Popen(["pipenv", "install"], cwd = Path(repopath())).wait()    

if args.createdist:
    reponame = args.createdist    
    subprocess.Popen(["pipenv", "run", "python", "setup.py", "sdist", "bdist_wheel"], cwd = Path(repopath())).wait()    

if args.twine:
    reponame = args.twine
    subprocess.Popen(["pipenv", "run", "python", "-m", "twine", "upload", "dist/*"], cwd = Path(repopath())).wait()    

if args.twinever:
    reponame = args.twinever
    curver = read_string_from_file(repofilepath("VER"), "0.0.1")
    subprocess.Popen(["pipenv", "run", "python", "-m", "twine", "upload", "dist/{}-{}*".format(reponame, curver)], cwd = Path(repopath())).wait()    

if args.setup:
    reponame = args.setup
    path = str(Path("repos/{}.json".format(reponame)))    
    configjson = readrepoconfigjson()
    idepath = str(Path(configjson["idepath"]))
    print("opening", path, "with", idepath)
    subprocess.Popen([idepath, path])

if args.code:
    reponame = args.code
    configjson = readrepoconfigjson()
    idepath = str(Path(configjson["idepath"]))
    subprocess.Popen([idepath, "."], cwd = str(Path(repopath())))

if args.updatever:
    reponame = args.updatever
    ver = args.ver
    print("updating {} version to {}".format(reponame, ver))
    metayaml = read_string_from_file(repofilepath("meta.yaml"), "")
    parts = metayaml.split("version:")
    parts = parts[1].split('"')
    curver = parts[1]
    print("current version", curver)
    newmetayaml = metayaml.replace('version: "{}"'.format(curver), 'version: "{}"'.format(ver))
    newmetayaml = newmetayaml.replace('git_rev: v{}'.format(curver), 'git_rev: v{}'.format(ver))    
    write_string_to_file(repofilepath("meta.yaml"), newmetayaml)
    setuppy = read_string_from_file(repofilepath("setup.py"), "")
    newsetuppy = setuppy.replace("version='{}'".format(curver), "version='{}'".format(ver))
    write_string_to_file(repofilepath("setup.py"), newsetuppy)
    write_string_to_file(repofilepath("VER"), ver)

