var Data = {

	githubRepos: '',

	init: function() {
		this.githubRepos = __github_repos;
	},

	findGitHubRepo: function(name) {
		for(var repoName in this.githubRepos) {
			if(repoName == name) {
				return this.githubRepos[name];
			}
		}

		return false;
	}

};