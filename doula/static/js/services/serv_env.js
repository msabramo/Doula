var ServiceEnv = {

	init: function() {
		Data.init();

		this.bindToUIActions();
		this.bindToDataActions();
	},

	bindToUIActions: function() {
		$(".collapse").collapse({'parent': '#accordion2'});
	},

	bindToDataActions: function() {
		$('#add-pckg').on('click', function() {
			// show modal dialog of packages available on cheese prism
			// that are not on here
			$('#add-packages').modal();
		});

		$('.new-version-btn').on('click', this.showNewVersionModal);
	},

	showNewVersionModal: function() {
		var name = $(this).attr('data-name');
		var repo = Data.findGitHubRepo(name);
		// alextodo need to build the right modal information.
		console.log(repo);

		$('#push-to-cheese-modal').modal();
		return false;
	}
};

$(document).ready(function() {
	ServiceEnv.init();
});