"""
A simplified interface to the Github V3 domain
"""

from doula.cache import Cache
from doula.config import Config
from doula.util import *
import json

cache = Cache.cache()
# alextodo put this into the INI
domain = "http://api.code.corp.surveymonkey.com"
html_domain = "http://code.corp.surveymonkey.com"


def get_devmonkeys_repos():
    """
    Get the Dev Monkey repos from redis
    """
    repos_as_json = cache.get("devmonkeys_repos")

    if repos_as_json:
        return json.loads(repos_as_json)
    else:
        return []


def get_package_github_info(name):
    """
    Get the github repo details for a particular package
    """
    all_repos = get_devmonkeys_repos()

    for repo in all_repos:
        if comparable_name(repo['name']) == comparable_name(name):
            return repo

    return False


def get_service_github_repos(service):
    """
    Get the github repo details for the services packages
    """
    github_repos = {}
    all_repos = get_devmonkeys_repos()

    for pckg in service.packages:
        for r in all_repos:
            if comparable_name(r['name']) == comparable_name(pckg.name):
                github_repos[comparable_name(r['name'])] = r
                break

    return github_repos


def pull_tags(git_repo):
    """
    Pull the tags from git and they're corresponding sha's
    """
    vals = (domain, Config.get('doula.github_org'), git_repo['name'])
    url = "%s/repos/%s/%s/tags" % vals

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
    vals = (domain, Config.get('doula.github_org'), git_repo['name'])
    url = "%s/repos/%s/%s/branches" % vals
    github_branches = json.loads(pull_url(url))
    branches = []

    for b in github_branches:
        branch = {"name": b["name"], "sha": b["commit"]["sha"]}

        # Pull the last 50 sha's for each branch
        vals = (domain, Config.get('doula.github_org'), git_repo['name'], branch["sha"])
        url = "%s/repos/%s/%s/commits?per_page=50&sha=%s" % vals

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


def pull_commit_branches(commit, branches):
    """
    Discover which branches this commit belongs to. Look back 50 commits.
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
    vals = (domain, Config.get('doula.github_org'), git_repo['name'])
    url = "%s/repos/%s/%s/commits" % vals

    commits = []
    git_commits = json.loads(pull_url(url))

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

        if cmt.get("author"):
            commit["author"]["login"] = cmt["author"]["login"],
            commit["author"]["avatar_url"] = cmt["author"]["avatar_url"]

        commit["branches"] = pull_commit_branches(commit, branches)

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
        [{
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
        ]
    """
    repos = []
    url = domain + '/orgs/' + Config.get('doula.github_org') + '/repos'
    git_repos = json.loads(pull_url(url))

    for git_repo in git_repos:
        tags = pull_tags(git_repo)
        branches = pull_branches(git_repo)
        commits = pull_commits(git_repo, tags, branches)

        repo = {
            "name": git_repo["name"],
            "html_url": git_repo["html_url"],
            "ssh_url": git_repo["ssh_url"],
            "org": Config.get('doula.github_org'),
            "domain": domain,
            "html_domain": html_domain,
            "tags": tags,
            "branches": branches,
            "commits": commits
        }

        repos.append(repo)

    return repos
