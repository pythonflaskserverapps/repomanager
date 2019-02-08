from github import Github
import time

# using username and password
g = Github("pythonflaskserverapps", "")

def listrepos(u):
    for repo in u.get_repos():
        print(repo.name)

u = g.get_user()

try:
    u.create_repo("test")
except:
    pass

listrepos(u)
    
r = u.get_repo("test")

print(r)

r.delete()

time.sleep(5)

listrepos(u)