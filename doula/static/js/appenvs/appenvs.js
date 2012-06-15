var AppEnv = {

	init: function() {
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

		$('.new-version-btn').on('click', function() {
			$('#push-to-cheese-modal').modal();
		});
	}
};

$(document).ready(function() {
	AppEnv.init();
});