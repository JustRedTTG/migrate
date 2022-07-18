import os, shutil
from save_load import *

def ask(message):
    print(message,end=" [Y/N] : ")
    result = input()
    if result in "Yy": return True
    elif result in "Nn": return False
    else:
        print("Unknown character, defaulting to NO")
        return False


def clear():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')


def git(folder):
    os.chdir(folder)
    os.system('git init --quiet')

no_git = False

# Check git presence
if not os.path.exists('test git'): os.mkdir('test git')
git('test git')
if not os.path.exists('.git'): no_git = True
os.chdir('..')
shutil.rmtree('test git')

if no_git:
    print("Sorry, we tried, but it seems you're missing git.")
    exit()
else: print("Confirmed the presence of git!")

data = load('save')

if data:
    print("Importing saved preferences.")
    local_folder = data[0]
    git_folder = data[1]
    gitignore = data[2]
else:
    local_folder = input("Local folder: ")
    git_folder = input("Git folder: ")
    gitignore = input("Git ignore: ")
    if ask("Save?"): save('save',local_folder, git_folder,gitignore)

print(f"\nTransferring all projects from: {local_folder}\n"
      f"To git folder: {git_folder}\n")
if not ask("You'll be asked to select which projects, is that okay?"): exit()

clear()

print("Initializing...")

projects = []
projects_git = []
ignore = []
imposter = []
valid = []

# List both local and git projects
for item in os.listdir(local_folder):
    if os.path.isdir(os.path.join(local_folder, item)): projects.append(item)

print(f"Found {len(projects)} local projects!")

for item in os.listdir(git_folder):
    if os.path.isdir(os.path.join(git_folder, item)): projects_git.append(item)

print(f"Found {len(projects_git)} git projects!")

# Check for duplicates
for item in projects:
    if item in projects_git: ignore.append(item)

print(f"Found {len(ignore)} duplicates.")

# Check for imposters and valid
for item in projects:
    if os.path.isdir(os.path.join(local_folder, item, ".git")): imposter.append(item)

print(f"Found {len(imposter)} imposters.")
for item in projects_git:
    if os.path.isdir(os.path.join(git_folder, item, ".git")): valid.append(item)
    else:
        for item2 in os.listdir(os.path.join(git_folder, item)):
            if os.path.isdir(os.path.join(git_folder, item, item2, ".git")): valid.append(item)

print(f"{len(valid)}/{len(projects_git)} projects are valid git projects.\n")
for item in projects_git:
    if not item in valid: print(item)

if not ask("Continue to select?"): exit()

i = 0
while i < len(projects):
    if projects[i] in projects_git: del projects[i]
    else: i += 1


clear()

# Selection menu
selection = set()
check = '☑'
no_check = '☐'
migrate = load('migrate')

if migrate:
    print('Found previous migrate selection.')
    if ask('Load it?'):
        for select in migrate[0]:
            if select in projects: selection.add(projects.index(select))
        os.remove('migrate')
while True:
    print(f'[0] - All - {check if len(selection) == len(projects) else no_check}')

    for i in range(len(projects)):
        print(f'[{i+1}] - {projects[i]} - {check if i in selection else no_check}')
    print("\nType END to finish the selection.\n"
          "Type the index number again to deselect\n",
          end="Select: ")
    inp = input()
    if inp == 'END': break
    index = int(inp)
    if 0 < index <= len(projects):
        if not index-1 in selection:
            selection.add(index-1)
        else: selection.remove(index-1)
    elif index == 0:
        full = len(selection) == len(projects)
        selection.clear()
        if full: continue
        for i in range(len(projects)): selection.add(i)

    clear()
clear()
complete_selection = []
for i in selection:
    print(projects[i])
    complete_selection.append(projects[i])

print("Look over the projects above.")

if not ask("Migrate?"):
    save('migrate', complete_selection)
    exit()

clear()

for i in selection:
    old_folder = os.path.join(local_folder, projects[i])
    new_folder = os.path.join(git_folder, projects[i])

    if os.path.exists(new_folder): shutil.rmtree(new_folder)

    shutil.copytree(old_folder, new_folder)
    git(new_folder)
    shutil.copy(gitignore,os.path.join(new_folder, '.gitignore'))
    print(f"migrate {projects[i]} : {old_folder} => {new_folder}")

print()

if not ask("Use github?"): exit()

for i in selection:
    new_folder = os.path.join(git_folder, projects[i])
    config = os.path.join(git_folder, projects[i],'.git','config')
    mtime = os.path.getmtime(config)

    print(f'Running: github open "{new_folder}"')
    os.system(f'github open "{new_folder}"')

    new_mtime = mtime
    while new_mtime == mtime:
        new_mtime = os.path.getmtime(config)



input("Press enter to exit")