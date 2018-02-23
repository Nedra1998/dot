#!/usr/bin/python3
"""
Backup.py

Syncs files, and commands from specified formats. Thus when a new system is
created, all of the files can easily be cloned to their required locations.
"""

import argparse
import apt
import shlex
import subprocess
import os
import json
import shutil


def load_data():
    """ Loads config file, containing all the relevant information for the
    backup."""
    if os.path.exists("conf.json"):
        return json.load(open("conf.json"))
    return {'files': [], 'dirs': [], 'cmds': [], 'pkgs': [], 'repos': []}


def save_data(conf):
    """ Save config file, with all of the information for the backup."""
    for key, value in conf.items():
        conf[key] = sorted(value)
    json.dump(conf, open("conf.json", 'w'))


def get_packages():
    return apt.Cache()


def package_installed(cache, name):
    if name not in cache:
        return False
    elif cache[name].is_installed:
        return True
    else:
        return False


def get_file_age(conf):
    for value in conf['files']:
        if os.path.exists(value[0]):
            value.append(os.stat(value[0]).st_mtime)
        else:
            value.append(0)
        # Remove??
        local_path = os.path.join(os.path.dirname(
            __file__), os.path.basename(value[0]))
        if os.path.exists(local_path):
            if value[1] != os.stat(local_path).st_mtime:
                value[1] = os.stat(local_path).st_mtime
        else:
            value[1] = 0
    for value in conf['dirs']:
        if os.path.exists(value[0]):
            value.append(os.stat(value[0]).st_mtime)
        else:
            value.append(0)
        # Remove??
        local_path = os.path.join(os.path.dirname(
            __file__), os.path.basename(value[0]))
        if os.path.exists(local_path):
            if value[1] != os.stat(local_path).st_mtime:
                value[1] = os.stat(local_path).st_mtime
        else:
            value[1] = 0


def get_repo_age(conf):
    for value in conf['repos']:
        if os.path.exists(value[1]):
            behind = False
            push = False
            if subprocess.run(shlex.split('git --git-dir ' + value[1] + '/.git fetch --dry-run'),
                              stdout=subprocess.PIPE).stdout.decode('utf-8') != str():
                behind = True
            current_branch = subprocess.run(shlex.split(
                "git --git-dir " + value[1] + "/.git rev-parse --abbrev-ref HEAD"), stdout=subprocess.PIPE).stdout.decode('utf-8')
            if subprocess.run(shlex.split(
                    'git --git-dir ' + value[1] + '/.git rev-list HEAD...origin/' + current_branch + ' --ignore-submodules --count'), stdout=subprocess.PIPE).stdout.decode('utf-8') != '0\n':
                push = True
            if behind is True and push is True:
                value.append(1)
            elif behind is True and push is False:
                value.append(2)
            elif behind is False and push is True:
                value.append(3)
            elif behind is False and push is False:
                value.append(0)
        else:
            value.append(-1)


def remove_age(conf):
    for value in conf['files']:
        if len(value) == 3:
            del value[-1]
    for value in conf['dirs']:
        if len(value) == 3:
            del value[-1]
    for value in conf['repos']:
        if len(value) == 3:
            del value[-1]


def should_add_data(args):
    if args.file is not None or args.cmd is not None or args.pkg is not None or args.dir is not None or args.repo is not None:
        return True
    return False


def add_data(args):
    conf = load_data()
    print(args)
    if args.remove is False:
        if args.file is not None:
            conf['files'] += [[x, 0] for x in args.file]
        elif args.cmd is not None:
            conf['cmds'] += args.cmd
        elif args.pkg is not None:
            conf['pkgs'] += args.pkg
        elif args.repo is not None:
            repos = list()
            for i in range(0, len(args.repo), 2):
                if i + 1 < len(args.repo):
                    repos.append([args.repo[i], args.repo[i + 1]])
                else:
                    repos.append([args.repo[i], os.path.join(
                        os.path.expanduser('~'), os.path.basename(args.repo[i]))])
            conf['repos'] += repos
        elif args.dir is not None:
            conf['dirs'] += [[x, 0] for x in args.dir]
    else:
        if args.file is not None:
            conf['files'] = [x for x in conf['files'] if x[0] not in args.file]
            for file in args.file:
                if os.path.exists(os.path.join(os.path.dirname(__file__), os.path.basename(file))):
                    os.remove(os.path.join(os.path.dirname(
                        __file__), os.path.basename(file)))
        if args.cmd is not None:
            conf['cmds'] = [x for x in conf['cmds'] if x not in args.cmd]
        if args.pkg is not None:
            conf['pkgs'] = [x for x in conf['pkgs'] if x not in args.pkg]
        if args.repo is not None:
            repos = list()
            for i in range(0, len(args.repo), 2):
                if i + 1 < len(args.repo):
                    repos.append([args.repo[i], args.repo[i + 1]])
                else:
                    repos.append([args.repo[i], os.path.join(
                        os.path.expanduser('~'), os.path.basename(args.repo[i]))])
            conf['repos'] = [x for x in conf['repos'] if x not in repos]
        if args.dir is not None:
            conf['dirs'] = [x for x in conf['dirs'] if x[0] not in args.dir]
            for dir in args.dir:
                if os.path.exists(os.path.join(os.path.dirname(__file__), os.path.basename(dir))):
                    shutil.rmtree(os.path.join(os.path.dirname(
                        __file__), os.path.basename(dir)))
    save_data(conf)


def list_data(color, uni):
    conf = load_data()
    get_file_age(conf)
    get_repo_age(conf)
    if len(conf['pkgs']) != 0:
        cache = get_packages()
    if color:
        print("\033[1mBackup Actions\033[0m\n")
    else:
        print("Backup Actions\n")
    for key, value in conf.items():
        print("{}:\n  ".format(key.title()), end='')
        if len(value) != 0:
            if key == "files" or key == "dirs":
                update = [y - z for x, y, z in value]
                if uni is True and key == "files":
                    value = [
                        "\uf15b " + os.path.relpath(x, os.path.expanduser('~')) for x, y, z in value]
                elif uni is True and key == "dirs":
                    value = [
                        "\ue5ff " + os.path.relpath(x, os.path.expanduser('~')) for x, y, z in value]
                else:
                    value = [os.path.relpath(
                        x, os.path.expanduser('~')) for x, y, z in value]
            elif key == "pkgs":
                update = [-1 if package_installed(cache, x)
                          is False else 0 for x in value]
                if uni is True:
                    value = ["\uf487 " + x for x in value]
            elif key == "repos":
                update = [z for x, y, z in value]
                if uni is True:
                    value = ["\uf401 " + '/'.join(x.split('/')[-2:])
                             for x, y, z in value]
                else:
                    value = ['/'.join(x.split('/')[-2:])
                             for x, y, z in value]
            else:
                update = [0] * len(value)
                if uni is True:
                    value = ["\ue24f " + x for x in value]
            widest = max(len(x) for x in value)
            padded = [x.ljust(widest) for x in value]
            perline = (int(os.popen('stty size', 'r').read().split()
                           [1]) - 4) // (widest + 2)
            print
            for i, col in enumerate(padded):
                if color and update[i] < 0:
                    print("\033[31m{}\033[0m".format(col), end='  ')
                elif update[i] < 0:
                    print("* {} *".format(col), end='  ')
                elif color and update[i] == 0:
                    print("\033[32m{}\033[0m".format(col), end='  ')
                elif update[i] == 0:
                    print("{}".format(col), end='  ')
                elif color and update[i] > 0 and key != "repos":
                    print("\033[33m{}\033[0m".format(col), end='  ')
                elif color and update[i] > 0 and key == "repos":
                    if update[i] == 1:
                        print("\033[35m{}\033[0m".format(col), end='  ')
                    elif update[i] == 2:
                        print("\033[33m{}\033[0m".format(col), end='  ')
                    elif update[i] == 3:
                        print("\033[34m{}\033[0m".format(col), end='  ')
                else:
                    print("{}".format(col), end='  ')
                if perline == 0 or i % perline == perline - 1:
                    if i != len(padded) - 1:
                        print('\n  ', end='')
        else:
            if color:
                print("\033[90mNone\033[0m", end='')
            else:
                print("None", end='')
        print()
    print()


def generate_folder(path):
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))


def col_uni_print(string, color_str, uni_str, color, uni, end='\n'):
    print_str = string
    if color:
        print_str = color_str + print_str + "\033[0m"
    if uni:
        if isinstance(uni_str, str):
            print_str = print_str.replace("_u_", uni_str)
        elif isinstance(uni_str, tuple):
            print_str = print_str.replace("_u_", uni_str[0])
        elif isinstance(uni_str, list):
            for uni_char in uni_str:
                if isinstance(uni_char, str):
                    print_str = print_str.replace("_u_", uni_char, 1)
                else:
                    print_str = print_str.replace("_u_", uni_char[0], 1)
    else:
        if isinstance(uni_str, str):
            print_str = print_str.replace("_u_", "")
        elif isinstance(uni_str, tuple):
            print_str = print_str.replace("_u_", uni_str[1])
        elif isinstance(uni_str, list):
            for uni_char in uni_str:
                if isinstance(uni_char, str):
                    print_str = print_str.replace("_u_", '', 1)
                else:
                    print_str = print_str.replace("_u_", uni_char[1], 1)
    print(print_str, end=end, flush=True)


def sync_files(color, uni):
    conf = load_data()
    get_file_age(conf)
    if color:
        print("\033[1mSyncing Files:\033[0m")
    else:
        print("Syncing Files:")
    did_work = False
    for value in conf['files']:
        if value[1] < value[2]:
            did_work = True
            col_uni_print("  _u_ Pulling \"{}\"...".format(
                value[0]), "\033[33m", ("\uf053 \uf15b", "<"), color, uni, end='')
            shutil.copy2(value[0], os.path.join(
                os.path.dirname(__file__), os.path.basename(value[0])))
            value[1] = value[2]
            col_uni_print("\033[2K\033[G  _u_ Pulling \"{}\"...  _u_".format(
                value[0]), "\033[32m", [("\uf053 \uf15b", "<"), ("\uf00c", "OK")], color, uni)
        elif value[1] > value[2]:
            did_work = True
            col_uni_print("  _u_ Pushing \"{}\"...".format(
                value[0]), "\033[33m", ("\uf054 \uf15b", ">"), color, uni, end='')
            generate_folder(value[0])
            shutil.copy2(os.path.join(os.path.dirname(__file__),
                                      os.path.basename(value[0])), value[0])
            col_uni_print("\033[2K\033[G  _u_ Pushing \"{}\"...  _u_".format(
                value[0]), "\033[34m", [("\uf054 \uf15b", ">"), ("\uf00c", "OK")], color, uni)
    if did_work is False:
        if color:
            print("  \033[90mNo files to sync\033[0m")
        else:
            print("  No files to sync")
    remove_age(conf)
    save_data(conf)


def sync_dirs(color, uni):
    conf = load_data()
    get_file_age(conf)
    if color:
        print("\033[1mSyncing Directories:\033[0m")
    else:
        print("Syncing Directories:")
    did_work = False
    for value in conf['dirs']:
        if value[1] < value[2]:
            did_work = True
            col_uni_print("  _u_ Pulling \"{}\"...".format(
                value[0]), "\033[33m", ("\uf053 \ue5ff", "<"), color, uni, end='')
            if os.path.exists(os.path.join(os.path.dirname(__file__), os.path.basename(value[0]))):
                shutil.rmtree(os.path.join(os.path.dirname(__file__),
                                           os.path.basename(value[0])))
            shutil.copytree(value[0], os.path.join(
                os.path.dirname(__file__), os.path.basename(value[0])))
            value[1] = value[2]
            col_uni_print("\033[2K\033[G  _u_ Pulling \"{}\"...  _u_".format(
                value[0]), "\033[32m", [("\uf053 \ue5ff", "<"), ("\uf00c", "OK")], color, uni)
        elif value[1] > value[2]:
            did_work = True
            col_uni_print("  _u_ Pushing \"{}\"...".format(
                value[0]), "\033[33m", ("\uf054 \ue5ff", ">"), color, uni, end='')
            generate_folder(value[0])
            shutil.copytree(os.path.join(os.path.dirname(
                __file__), os.path.basename(value[0])), value[0])
            col_uni_print("\033[2K\033[G  _u_ Pushing \"{}\"...  _u_".format(
                value[0]), "\033[34m", [("\uf054 \ue5ff", ">"), ("\uf00c", "OK")], color, uni)
    if did_work is False:
        if color:
            print("  \033[90mNo directories to sync\033[0m")
        else:
            print("  No directories to sync")
    remove_age(conf)
    save_data(conf)


def exec_cmd(cmd):
    result = subprocess.run(shlex.split(
        cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout_str = result.stdout.decode('utf-8')
    stderr_str = result.stderr.decode('utf-8')
    if stderr_str == "\nWARNING: apt does not have a stable CLI interface. Use with caution in scripts.\n\n":
        stderr_str = str()
    if stderr_str == str():
        return None
    else:
        stderr_str = "      " + stderr_str.replace("\n", "\n      ")
        stderr_str = stderr_str.rstrip()
        return stderr_str


def run_exec(color, uni):
    conf = load_data()
    if color:
        print("\033[1mRunning Commands:\033[0m")
    else:
        print("Running Commands:")
    if len(conf['cmds']) == 0:
        if color:
            print("  \033[90mNo commands to execute\033[0m")
        else:
            print("  No commands to execute")
        return
    for cmd in conf['cmds']:
        col_uni_print("  _u_ Running \"{}\"...".format(
            cmd), "\033[33m", "\ue24f", color, uni, end='')
        res = exec_cmd(cmd)
        if res is None:
            col_uni_print("\033[2K\033[G  _u_ Running \"{}\"...  _u_".format(
                cmd), "\033[32m", ["\ue24f", ("\uf00c", "OK")], color, uni)
        else:
            col_uni_print("\033[2K\033[G  _u_ Running \"{}\"...  _u_".format(
                cmd), "\033[31m", ["\ue24f", ("\uf071", "ERR")], color, uni)
            print(res)


def install_packages(color, uni):
    conf = load_data()
    if color:
        print("\033[1mInstalling Packages:\033[0m")
    else:
        print("Installing Packages:")
    if len(conf['pkgs']) == 0:
        if color:
            print("  \033[90mNo packages to install\033[0m")
        else:
            print("  No packages to install")
        return
    cache = get_packages()
    for pkg in conf['pkgs']:
        col_uni_print("  _u_ Installing \"{}\"...".format(
            pkg), "\033[33m", "\uf487", color, uni, end='')
        res = None
        if package_installed(cache, pkg) is False:
            res = exec_cmd("sudo apt install -y \"{}\"".format(pkg))
        if res is None:
            col_uni_print("\033[2K\033[G  _u_ Installing \"{}\"...  _u_".format(
                pkg), "\033[32m", ["\uf487", ("\uf00c", "OK")], color, uni)
        else:
            col_uni_print("\033[2K\033[G  _u_ Installing \"{}\"...  _u_".format(
                pkg), "\033[31m", ["\uf487", ("\uf071", "ERR")], color, uni)
            print(res)


def install_repos(color, uni):
    conf = load_data()
    if color:
        print("\033[1mInstalling Repositories:\033[0m")
    else:
        print("Intalling Repositories:")
    if len(conf['repos']) == 0:
        if color:
            print("  \033[90mNo repositories to install\033[0m")
        else:
            print("  No repositories to install")
        return
    get_repo_age(conf)
    for repo in conf['repos']:
        if repo[2] == -1:
            col_uni_print("  _u_ Cloning \"{}\"...".format('/'.join(repo[0].split('/')[-2:])),
                          "\033[33m", "\uf401", color, uni, end='')
            res = exec_cmd("git clone {} {}".format(repo[0], repo[1]))
            if res is None:
                col_uni_print("\033[2K\033[G  _u_ Cloning \"{}\"...  _u_".format(
                    '/'.join(repo[0].split('/')[-2:])), "\033[32m",
                    ["\uf401", ("\uf00c", "OK")], color, uni)
            else:
                col_uni_print("\033[2K\033[G  _u_ Cloning \"{}\"...  _u_".format(
                    '/'.join(repo[0].split('/')[-2:])), "\033[32m",
                    ["\uf401", ("\uf00c", "OK")], color, uni)
                print(res)
        elif repo[2] == 1:
            col_uni_print("  _u_ Pulling \"{}\"...  _u_".format('/'.join(repo[0].split('/')[-2:])),
                          "\033[33m", ["\uf401", ("\uf071", "ERR")], color, uni)
            print("    Please preform merge manualy at \"{}\"".format(repo[1]))
        elif repo[2] == 2:
            col_uni_print("  _u_ Pulling \"{}\"...".format('/'.join(repo[0].split('/')[-2:])),
                          "\033[33m", "\uf401", color, uni, end='')
            res = exec_cmd("git --git-dir {} pull".format(repo[1]))
            if res is None:
                col_uni_print("\033[2K\033[G  _u_ Pulling \"{}\"...  _u_".format(
                    '/'.join(repo[0].split('/')[-2:])), "\033[32m",
                    ["\uf401", ("\uf00c", "OK")], color, uni)
            else:
                col_uni_print("\033[2K\033[G  _u_ Pulling \"{}\"...  _u_".format(
                    '/'.join(repo[0].split('/')[-2:])), "\033[32m",
                    ["\uf401", ("\uf00c", "OK")], color, uni)
                print(res)


def main():
    parser = argparse.ArgumentParser(
        description="File backup and restore system.")
    parser.add_argument('--version', action='version',
                        version='%(prog)s 1.0')
    parser.add_argument('-s', '--sync', action='store_true',
                        help='Syncs files to current repo.')
    parser.add_argument('-d', '--sync-dirs', action='store_true',
                        help="Syncs directores to current repo.")
    parser.add_argument('-x', '--exc', action='store_true',
                        help='Runs stored commands.')
    parser.add_argument('-i', '--install', action='store_true',
                        help='Installs stored repositories')
    parser.add_argument('-g', '--git', action='store_true',
                        help="Clones/pulls git repositories")
    parser.add_argument('-a', '--all', action='store_true',
                        help='Runs all restore actions')

    parser.add_argument('-l', '--list', action='store_true',
                        help='Lists all files, commands, repositories, and'
                        'directories that will be saved.')
    parser.add_argument('-c', '--color', action='store_true',
                        help='Adds colors indicating status.')
    parser.add_argument('-u', '--no-unicode', action='store_false',
                        help='Disables unicode characters for ASCII alt.')

    parser.add_argument('--file', nargs='*', help="Add file to repository")
    parser.add_argument('--cmd', nargs='*',
                        help="Add command to repository")
    parser.add_argument('--pkg', nargs='*',
                        help="Add package to repository")
    parser.add_argument('--repo', nargs='*', help="Add repo to repository")
    parser.add_argument('--dir', nargs='*',
                        help="Add directory to repository")
    parser.add_argument('-r', '--remove', action='store_true',
                        help="Removes all specified entries instead of adding them.")
    args = parser.parse_args()
    if args.repo:
        print(args)
    if should_add_data(args):
        add_data(args)
    if args.list is True:
        list_data(args.color, args.no_unicode)
    if args.install is True:
        install_packages(args.color, args.no_unicode)
    if args.git is True:
        install_repos(args.color, args.no_unicode)
    if args.exc is True:
        run_exec(args.color, args.no_unicode)
    if args.sync_dirs is True:
        sync_dirs(args.color, args.no_unicode)
    if args.sync is True:
        sync_files(args.color, args.no_unicode)
    if args.all is True:
        install_packages(args.color, args.no_unicode)
        install_repos(args.color, args.no_unicode)
        run_exec(args.color, args.no_unicode)
        sync_dirs(args.color, args.no_unicode)
        sync_files(args.color, args.no_unicode)


if __name__ == "__main__":
    main()
