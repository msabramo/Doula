var AppEnv = {

	init: function() {
		this.bindToUIActions();
		this.bindToDataActions();
	},

	bindToUIActions: function() {
		
	},

	bindToDataActions: function() {
		$('#add-pckg').on('click', function() {
			// show modal dialog of packages available on cheese prism
			// that are not on here
			$('#add-packages').modal();
		});
	}
}

$(document).ready(function() {
	AppEnv.init();
});