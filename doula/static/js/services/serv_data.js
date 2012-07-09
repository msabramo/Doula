var Data = {

	githubRepos: '',

	init: function() {
		// the service needs to have the github info as well
		_mixin(this, __service);
		console.log(this);
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