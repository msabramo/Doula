"""
A simplified interface to the GitHub V3 API
"""

from datetime import datetime
from doula.cache import Redis
from doula.cache_keys import key_val
from doula.config import Config
from doula.util import pull_json_obj, pull_url, find_package_and_version_in_pip_freeze_text, date_to_seconds_since_epoch, comparable_name, dumps
import base64
import pdb
import re
import simplejson as json
import sys
import time
import requests

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

######################
# PULL DOULA ADMINS
######################


def pull_doula_admins():
    """
    Doula admins have the ability to lockdown an entire site. This means
    no one else can release to this site unless they are an admin
    """
    url = build_url_to_api("%(domain)s/orgs/%(admins)s/members?access_token=%(token)s")

    members = pull_json_obj(url)

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

    git_tags = pull_json_obj(url)
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

        commits_for_branch = pull_json_obj(url)
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
    commits = []
    git_commits = []

    try:
        params = {"repo": git_repo['name']}
        url = build_url_to_api("%(domain)s/repos/%(packages)s/%(repo)s/commits", params)
        git_commits = pull_json_obj(url)
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

###################################
# Pull Deve Monkey Repos
###################################

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
    start = time.time()
    url = build_url_to_api("%(domain)s/orgs/%(packages)s/repos?access_token=%(token)s")
    git_repos = pull_json_obj(url)

    diff = time.time() - start

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
            "domain": Config.get('doula.github.api.domain'),
            "html_domain": Config.get('doula.github.html.domain'),
            "tags": tags,
            "branches": branches,
            "commits": commits
        }

        repos[comparable_name(repo["name"])] = repo

    diff = time.time() - start

    print "\nDIFF IN TIME FOR PULL ALL REPOS: " + str(diff)

    return repos

###################################
# Pull Releases for Service
###################################

def pull_releases_for_service(service):
    """
    Pull all the releases for this single service since this release date
    for all the services branches.
    Returns releases dict:
    {
        "mt1": {
            [
                {
                "author": author,
                "date: date,
                "branch: branch,
                "packages: packages,
                "commit_message: commit_message,
                "release_number: 0,
                "sha1: "",
                "sha1_etc: "",
                "site: branch,
                "service: "",
                "is_rollback: False,
                "production: False,
                "rolled_back_from_release_number: 0
            },
            {
                ...
            }]
        },
        "mt2": {
            [{
                ...
            },
            {
                ...
            }]
        }
    }
    """
    releases = {}

    branch_names = _pull_branches_for_service_releases(service)

    for branch_name in branch_names:
        print 'Finding commits for ' + branch_name
        releases[branch_name] = []

        # Pull the last 20 sha's for each branch
        url = "%(domain)s/repos/%(appenvs)s/%(repo)s/commits?sha=%(sha)s&per_page=20"
        params = {"repo": service, "sha": branch_name}
        url = build_url_to_api(url, params)
        commits_for_branch = pull_json_obj(url)

        print 'Number of commits for service: ' + str(len(commits_for_branch))

        # Every commit to this repo is a new release to the environment
        # and every child is an angel sans wings.
        for cmt in commits_for_branch:
            manifest = _pull_release_manifest(service, cmt["sha"])
            single_release = _build_release_dict_from_manifest_and_cmt(manifest, cmt, branch_name, service)
            releases[branch_name].append(single_release)

    return releases


def _pull_release_manifest(service, sha):
    """
    Attempt to find a doula.manifest file for a release.
    """
    try:
        url = "http://code.corp.surveymonkey.com/%(appenvs)s/%(repo)s/raw/%(sha)s/doula.manifest"
        params = {"repo": service, "sha": sha}
        url = build_url_to_api(url, params)
        manifest_as_json = pull_url(url)

        if manifest_as_json:
            return json.loads(manifest_as_json)
    except:
        pass
        # some of these don't have manifests. that's okay cause they're old
        # releases before we had manifets
        # print 'ERROR PULLING RELEASE MANIFEST'
        # print sys.exc_info()

    return {}


def _build_release_dict_from_manifest_and_cmt(manifest, cmt, branch_name, service):
    """
    Build a release from the manifest or the commit.
    Older release commits will not have a manifest so we do the best we can.

    The release dict with all keys below.
    """
    if len(manifest.keys()) > 0:
        return {
            "author": cmt["commit"]["author"]["email"],
            "date": cmt["commit"]["author"]["date"],
            "date_as_epoch": date_to_seconds_since_epoch(cmt["commit"]["author"]["date"]),
            "commit_message": cmt["commit"]["message"],
            "sha1_etc": manifest.get("sha1_etc", ""),
            "packages": _build_release_packages(manifest, cmt),
            "branch": branch_name,
            "site": branch_name,
            "service": service,
            "sha1": cmt["sha"],
            "is_rollback": manifest.get("is_rollback", False),
            "release_number": manifest.get("release_number", "0"),
            "production": manifest.get("production", False),
            "rolled_back_from_release_number": manifest.get("rolled_back_from_release_number", "0")
        }
    else:
        return {
            "author": cmt["commit"]["author"]["email"],
            "date": cmt["commit"]["author"]["date"],
            "date_as_epoch": date_to_seconds_since_epoch(cmt["commit"]["author"]["date"]),
            "commit_message": cmt["commit"]["message"],
            "sha1_etc": "",
            "packages": _build_release_packages({}, cmt),
            "branch": branch_name,
            "site": branch_name,
            "service": service,
            "sha1": cmt["sha"],
            "is_rollback": False,
            "release_number": "0",
            "production": False,
            "rolled_back_from_release_number": "0"
        }


def pull_repo_hooks(repo, owner='devmonkeys'):
    params = {'owner': owner, 'repo': repo}
    url = "%(domain)s/repos/%(owner)s/%(repo)s/hooks?access_token=%(token)s"
    url = build_url_to_api(url, params)
    print url
    val =  pull_json_obj(url)
    return val


def add_hook_to_repo(repo, callback_url, owner='devmonkeys'):
    params = {'owner': owner, 'repo': repo}
    url = "%(domain)s/repos/%(owner)s/%(repo)s/hooks?access_token=%(token)s"
    url = build_url_to_api(url, params)
    data = json.dumps({'name': 'web',
            'config':
                {'url':callback_url,
                 'content_type': 'json',
                 'secret':'sauce',
                 'insecure_ssl': 1
                 }
            })
    return post_url(url, data)


def all_repos_in_org(org):
    url = "%(domain)s/orgs/%(org)s/repos?access_token=%(token)s"
    url = build_url_to_api(url, {'org': org})
    return pull_json_obj(url)


def _build_release_packages(manifest, cmt):
    """Build packages from commit message or manifest"""

    if 'packages' in manifest:
        return manifest.get('packages', {})
    else:
        packages = {}

        for line in cmt["commit"]["message"].splitlines():
            package_and_version = find_package_and_version_in_pip_freeze_text(line)
            packages.update(package_and_version)

    return packages

def _pull_branches_for_service_releases(service):
    url = "%(domain)s/repos/%(appenvs)s/%(service)s/branches"
    url = build_url_to_api(url, {"service": service})
    github_branches = pull_json_obj(url)

    return [branch["name"] for branch in github_branches]

## End Pull releases for service

#############################
# Pull the Services from Git
#############################

def pull_appenv_service_names():
    """
    Pull appenv service names
    """
    url = build_url_to_api("%(domain)s/orgs/%(appenvs)s/repos?access_token=%(token)s")
    git_repos = pull_json_obj(url)

    return [git_repo["name"] for git_repo in git_repos]


###################################
# Pull Config for Service
###################################

def pull_config_services_with_branches():
    """
    Pull the configs repos from GitHub and all their branches

    Returns:
    [
        "service": "billweb",
        "branches": [
            {
                "site": "mt1",
                "sha": "17e6642dca429043725ad6a98ce966e5a67eac69"
            }
        ]
    ]
    """
    url = build_url_to_api("%(domain)s/orgs/%(config)s/repos?access_token=%(token)s")
    git_repos = pull_json_obj(url)
    names = []

    for repo in git_repos:
        branches = _find_pull_service_configs_branches(repo["name"])
        names.append({
            "service": repo["name"],
            "branches": branches
            })

    return names


def _find_pull_service_configs_branches(service):
    """
    Pull all the branches for a service config repo
    Each branch name corresponds to a site.
    """
    # Pull all the branches for each config repo
    url = "%(domain)s/repos/%(config)s/%(service)s/branches"
    url = build_url_to_api(url, {"service": service})

    github_branches = pull_json_obj(url)
    branches = []

    for b in github_branches:
        branch = {"site": b["name"], "sha": b["commit"]["sha"]}
        branches.append(branch)

    return branches


def pull_service_configs(site, service, sha='', date=''):
    """
    Pull all the latest commits for this service since this specific date.

    Returns the GitHub API response as a dict object, paired down
    See http://developer.github.com/v3/repos/commits/ for example output
    """
    service_configs = []
    git_service_configs = []

    try:
        # Our majestic URL. pull everything on the site branch
        url = "%(domain)s/repos/%(config)s/%(service)s/commits?"
        url += "access_token=%(token)s&per_page=30&sha=%(sha)s&since=%(since)s"
        params = {"service": service, "since": date, 'sha': site}
        url = build_url_to_api(url, params)

        git_service_configs = pull_json_obj(url)
    except:
        # Not all services have commits yet. Ignore those.
        pass

    for git_service_config in git_service_configs:
        service_configs.append({
            "site": site,
            "service": service,
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

def post_url(url, data, timeout=3.0):
    """
    Pull the URL text. Always raise the status error.
    """
    response = requests.post(url, data=data, timeout=timeout)
    # If the response is non 200, we raise an error
    response.raise_for_status()
    if response:
        return json.loads(response.text)
    else:
        return {}

def delete_url(url, timeout=3.0):
    """
    Pull the URL text. Always raise the status error.
    """
    response = requests.delete(url, timeout=timeout)
    # If the response is non 200, we raise an error
    response.raise_for_status()
    if response:
        return json.loads(response.text)
    else:
        return {}

