"""
A simplified interface to the Github V3 API
"""

from datetime import datetime
from doula.cache import Redis
from doula.config import Config
from doula.util import *
import simplejson as json
import re

######################
# PULL FROM CACHE
######################


def get_devmonkey_repo(name):
    redis = Redis.get_instance()
    repo_as_json = redis.get("repo.devmonkeys:" + comparable_name(name))

    if repo_as_json:
        return json.loads(repo_as_json)

    return False


def get_doula_admins():
    """
    Get the Doula admins from redis. if redis doesn't exist pull now
    """
    redis = Redis.get_instance()
    admins_as_json = redis.get("doula.admins")

    if admins_as_json:
        admins = json.loads(admins_as_json)
    else:
        admins = pull_doula_admins()
        redis.set('doula.admins', dumps(admins))

    return admins


def get_appenv_releases(name, branch):
    """
    Get the service releases. Each release is a commit
    to the repo
    Github data is in the format
    {
        "name of service": {
            "branches": {
                "mtx": {
                    "commits": {
                        [{
                            "date": "",
                            "message": "",
                            "author": ""
                        }]
                    }
                }
            }
        }
    }
    """
    redis = Redis.get_instance()
    json_text = redis.get("repos:appenvs")

    if json_text:
        github_appenv_data = json.loads(json_text)

        if name in github_appenv_data:
            branches = github_appenv_data[name]["branches"]

            if branch in branches:
                return branches[branch]["commits"]

    return {}

######################
# PULL DOULA ADMINS
######################


def pull_doula_admins():
    """
    Doula admins have the ability to lockdown an entire site. This means
    no one else can release to this site unless they are an admin
    """
    url = build_url_to_api("%(domain)s/orgs/%(admins)s/members?access_token=%(token)s")

    members = json.loads(pull_url(url))

    return [member['login'] for member in members]

######################
# PULL DEVMONKEY REPOS FROM GITHUB
######################


def get_package_github_info(name):
    """
    Get the github repo details for a particular package
    """
    return get_devmonkey_repo(name)


def get_service_github_repos(service):
    """
    Get the github repo details for the services packages
    """
    github_repos = {}

    for pckg in service.packages:
        repo = get_devmonkey_repo(pckg.comparable_name)

        if repo:
            github_repos[pckg.comparable_name] = repo

    return github_repos


def pull_tags(git_repo):
    """
    Pull the tags from git and they're corresponding sha's
    """
    url = "%(domain)s/repos/%(packages)s/%(repo)s/tags"
    url = build_url_to_api(url, {"repo": git_repo["name"]})

    git_tags = json.loads(pull_url(url))
    tags = []

    for tag in git_tags:
        tags.append({
            'name': tag['name'],
            'sha': tag['commit']['sha']
        })

    return tags


def pull_branches(git_repo):
    """
    Pull the branches from the github repo
    """
    url = "%(domain)s/repos/%(packages)s/%(repo)s/branches"
    url = build_url_to_api(url, {"repo": git_repo['name']})

    github_branches = json.loads(pull_url(url))
    branches = []

    for b in github_branches:
        branch = {"name": b["name"], "sha": b["commit"]["sha"]}

        # Pull the last 50 sha's for each branch
        url = "%(domain)s/repos/%(packages)s/%(repo)s/commits?per_page=50&sha=%(sha)s"
        url = build_url_to_api(url, {"repo": git_repo["name"], "sha": branch["sha"]})

        commits_for_branch = json.loads(pull_url(url))
        shas = []

        for cmt in commits_for_branch:
            shas.append(cmt["sha"])

        branch["shas"] = shas
        branches.append(branch)

    return branches


def pull_package_version(commit, tags):
    """
    This github commit is a 'bump version' commit that pulls the
    """
    package_version = ""

    for tag in tags:
        if tag["sha"] == commit["sha"]:
            package_version = re.sub(r'^v', '', tag["name"], flags=re.I)
            break

    return package_version


def find_branches_commit_belongs_to(commit, branches):
    """
    Find which branches this commit belongs to.
    The each branch in the branches list contains a list of
    the last 50 sha's.
    """
    commit_branches = []

    for branch in branches:
        if commit["sha"] in branch["shas"]:
            commit_branches.append({
                "name": branch["name"],
                "sha": branch["sha"]
            })

    return commit_branches


def pull_commits(git_repo, tags, branches):
    """
    Pull the latest commits for this repo. We'll build a commit dict
    that has all the values we need including branch, and package version

    We build a commit dict that looks like this:
    {
        "sha": "...",
        "author": {
            "name": "name of author",
            "email": "email address",
            "date": "date of commit",

        },
        "message": "...",
        "branches": [
            {
                "name": "",
                "sha": ""
            }
        ]
        # version only exist if the commit is a bump version commit
        "package_version": "0.2.3"
    }
    """
    params = {"repo": git_repo['name']}
    url = build_url_to_api("%(domain)s/repos/%(packages)s/%(repo)s/commits", params)

    commits = []
    git_commits = []

    try:
        git_commits = json.loads(pull_url(url))
    except:
        # Some repos may not have the details, ignore and move on
        pass

    for cmt in git_commits:
        commit = {
            "sha": cmt["sha"],
            "author": {
                "name": cmt["commit"]["author"]["name"],
                "email": cmt["commit"]["author"]["email"],
                "date": cmt["commit"]["author"]["date"],
                "login": "unknown",
                "avatar_url": "http://code.corp.surveymonkey.com/images/gravatars/gravatar-140.png"
            },
            "date": cmt["commit"]["author"]["date"],
            "message": cmt["commit"]["message"],
            "package_version": ""
        }

        # if no date. use today's date cause we can't have a blank for this field
        if not commit["date"]:
            commit["date"] = datetime.now().strftime("%a, %d %b %Y %H:%M:%S")

        if cmt.get("author"):
            commit["author"]["login"] = cmt["author"]["login"],
            commit["author"]["avatar_url"] = cmt["author"]["avatar_url"]

        commit["branches"] = find_branches_commit_belongs_to(commit, branches)

        # still need the branches that this commit belongs to

        # bump versions are doula commits that created
        if commit["message"] == 'bump version':
            commit["package_version"] = pull_package_version(commit, tags)

        commits.append(commit)

    return commits


def pull_devmonkeys_repos():
    """
    Pull Dev Monkey repos
    Returns datastructure:
        {
        "name": {
        "name":[name of project],
        "html_url":[url to github page of project],
        "ssh_url":[git ssh url],
        "org": [name of org],
        "domain": [domain],
        "tags":[{
            "name":[name of tag],
            "commit_hash": [hash of tag]
            }],
        "branches":[{
            "name": [name of branch]
            }]
        },
        "commits": [
            {
                "sha": "...",
                "author": {
                    "name": "name of author",
                    "email": "email address",
                    "date": "date of commit"
                },
                "message": "...",
                "branches": [
                    {
                        "name": "",
                        "sha": ""
                    }
                ]
                # version only exist if the commit is a bump version commit
                "package_version": "0.2.3"
            }
            ]
        }
    """
    repos = {}
    # todo: pass in the previous git commit. and only pull from there
    # pass in the param sha=[sha]
    # see http://developer.github.com/v3/repos/commits/
    start = time.time()

    url = build_url_to_api("%(domain)s/orgs/%(packages)s/repos?access_token=%(token)s")
    repos_as_json = pull_url(url)
    git_repos = json.loads(repos_as_json)

    diff = time.time() - start
    print "\n"
    print 'DIFF IN TIME FOR PULL REPOS: ' + str(diff)

    for git_repo in git_repos:
        print 'PULLING GIT REPO: ' + git_repo["name"]

        tags = pull_tags(git_repo)
        branches = pull_branches(git_repo)
        commits = pull_commits(git_repo, tags, branches)

        repo = {
            "name": git_repo["name"],
            "html_url": git_repo["html_url"],
            "ssh_url": git_repo["ssh_url"],
            "org": Config.get('doula.github.packages.org'),
            "domain": domain,
            "html_domain": Config.get('doula.github.html.domain'),
            "tags": tags,
            "branches": branches,
            "commits": commits
        }

        repos[comparable_name(repo["name"])] = repo

    diff = time.time() - start
    print "\n"
    print 'DIFF IN TIME FOR PULL ALL REPOS: ' + str(diff)

    return repos


######################
# PULL APPLICATION ENVS FROM GITHUB
######################


def pull_appenv_branches(git_repo):
    """
    Pull the commits for the appenvs for every one of their branches
    Format of response:
        "mt1": {
            "commits": [
                    {
                        "date": "2012-06-04T20:14:01+00:00",
                        "message": "Pushed autocompletesvc==0.2.2"
                    }
                ]
        }
    """
    url = "%(domain)s/repos/%(appenvs)s/%(repo)s/branches"
    url = build_url_to_api(url, {"repo": git_repo['name']})

    github_branches = json.loads(pull_url(url))
    branches = {}

    for github_branch in github_branches:
        branches[github_branch["name"]] = {
            "commits": []
        }

        # Pull the last 20 sha's for each branch
        url = "%(domain)s/repos/%(appenvs)s/%(repo)s/commits?per_page=20&sha=%(sha)s"
        params = {"repo": git_repo['name'], "sha": github_branch["commit"]["sha"]}
        url = build_url_to_api(url, params)

        commits_for_branch = json.loads(pull_url(url))

        # Every commit to this branch and repo is a new
        # release to the environment
        for cmt in commits_for_branch:
            commit = {
                "author": cmt["commit"]["author"]["email"],
                "date": cmt["commit"]["author"]["date"],
                "message": cmt["commit"]["message"]
            }

            branches[github_branch["name"]]["commits"].append(commit)

    return branches

###################################
# Pull App Env
# TODO: pull the application env.
# pull doula.manifest
# pull from the latest date
# pull the config file commits too.
###################################


def pull_appenv_repos():
    """
    Pull the appenv repos in this format.
    [
    {
        "branches": {
            "mt1": {
                "commits": [
                        {
                            "date": "2012-06-04T20:14:01+00:00",
                            "message": "Pushed autocompletesvc==0.2.2"
                        }
                    ]
            }
        },
        "name": "acsvc"
    },
    ]
    """
    repos = {}
    url = build_url_to_api("%(domain)s/orgs/%(appenvs)s/repos?access_token=%(token)s")

    git_repos = json.loads(pull_url(url))

    for git_repo in git_repos:
        repos[git_repo["name"]] = {
            "name": git_repo["name"],
            "branches": pull_appenv_branches(git_repo)
        }

    return repos


###################################
# Pull Config for Service
###################################

def pull_services_for_config_names():
    """
    Pull the configs repos from GitHub
    """
    url = build_url_to_api("%(domain)s/orgs/%(config)s/repos?access_token=%(token)s")
    git_repos = json.loads(pull_url(url))
    names = []

    for repo in git_repos:
        names.append(repo["name"])

    return names

def pull_service_configs(name, date=''):
    """
    Pull all the latest commits for this service since this specific date.

    Returns the GitHub API response as a dict object, paired down
    See http://developer.github.com/v3/repos/commits/ for example output
    """
    # alextodo. you also have to pull the branches. each service needs a branch too.
    # fuck me
    url = "%(domain)s/repos/%(config)s/%(name)s/commits?per_page=10&since=%(since)s"
    params = {"name": name, "since": date}
    url = build_url_to_api(url, params)

    git_service_configs = []

    try:
        config_as_json = pull_url(url)
        git_service_configs = json.loads(config_as_json)
    except:
        # Not all services have commits yet. Ignore those.
        pass

    service_configs = []

    print 'length of the commits: ' + str(len(service_configs))

    for git_service_config in git_service_configs:
        service_configs.append({
            "name": name,
            "date": git_service_config["commit"]["committer"]["date"],
            "sha" : git_service_config["sha"],
            "author": git_service_config["commit"]["author"]["email"],
            "message": git_service_config["commit"]["message"]
        })

    return service_configs


def build_url_to_api(url, params={}):
    """
    String formats a URL to the GitHub API. Always adds the
    domain and token to the URL.

    params is a dict.
    """
    params["domain"]   = Config.get('doula.github.api.domain')
    params["token"]    = Config.get('doula.github.token')
    params["appenvs"]  = Config.get('doula.github.appenvs.org')
    params["config"]   = Config.get('doula.github.config.org')
    params["packages"] = Config.get('doula.github.packages.org')
    params["admins"]   = Config.get('doula.github.doula.admins.org')

    return url % params
