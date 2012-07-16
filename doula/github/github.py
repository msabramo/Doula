"""
A simplified interface to the Github V3 API
"""

from doula.cache import Cache
from doula.config import Config
from doula.util import *
import json

cache = Cache.cache()
api = "http://api.code.corp.surveymonkey.com"


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


def pull_devmonkeys_repos():
    """
    Pull Dev Monkey repos
    Returns datastructure:
        [{
        "name":[name of project],
        "html_url":[url to github page of project],
        "ssh_url":[git ssh url],
        "tags":[{
            "name":[name of tag],
            "commit_hash": [hash of tag]
            }],
        "branches":[{
            "name": [name of branch]
            }]
        }]
    """
    repos = []
    url = api + '/orgs/' + Config.get('doula.github_org') + '/repos'
    git_repos = json.loads(pull_url(url))

    for git_repo in git_repos:
        # Pull the tags from github
        tags = []
        tag_url = api + '/repos/' + Config.get('doula.github_org')
        tag_url += '/' + git_repo['name'] + '/tags'
        git_tags = json.loads(pull_url(tag_url))

        for git_tag in git_tags:
            tag = {
                'name': git_tag['name'],
                'commit_hash': git_tag['commit']['sha']
            }

            tags.append(tag)

        # Pull the branches from github
        branches = []
        branch_url = api + '/repos/devmonkeys/'
        branch_url += git_repo['name'] + '/branches'
        git_branches = json.loads(pull_url(branch_url))

        for git_branch in git_branches:
            branch = {"name": git_branch["name"]}
            branches.append(branch)

        repo = {
            "name": git_repo["name"],
            "html_url": git_repo["html_url"],
            "ssh_url": git_repo["ssh_url"],
            "tags": tags,
            "branches": branches
        }

        repos.append(repo)

    return repos
