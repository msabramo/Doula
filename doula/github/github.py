"""
A simplified interface to the Github V3 API
"""

from doula.cache import Cache
from doula.util import *
import json

cache = Cache.cache()
# what's the Doula user? we need the details for that.
user = "surveymonkey"
token = "bf51a7224a9baf757bc12923e0a81561"
api = "http://api.code.corp.surveymonkey.com"


def get_devmonkeys_repos():
    """
    Get the Dev Monkey repos from redis
    """
    return json.loads(cache.get("devmonkeys_repos"))


def get_service_github_repos(service):
    """
    Get the github repo details for the services packages
    """
    github_repos = {}
    all_repos = get_devmonkeys_repos()

    for pckg in service.packages:
        for r in all_repos:
            if clean_for_compare(r['name']) == clean_for_compare(pckg.name):
                github_repos[r['name']] = r
                break

    return github_repos


def pull_devmonkeys_repos():
    """
    Pull Dev Monkey repos
    Returns datastructure:
        [{
        "name":[name of project],
        "html_url":[url to github page of project],
        "git_url":[git hub repo page of project],
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
    url = api + '/orgs/devmonkeys/repos'
    git_repos = json.loads(pull_url(url))

    for git_repo in git_repos:
        # Pull the tags from github
        tags = []
        tag_url = api + '/repos/devmonkeys/' + git_repo['name'] + '/tags'
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
            "git_url": git_repo["git_url"],
            "tags": tags,
            "branches": branches
        }

        repos.append(repo)

    return repos
