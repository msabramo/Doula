var ServiceEnv = {

	init: function() {
		_mixin(this, AJAXUtil);
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

		$('.new-version-btn').on('click', _bind(this.showNewVersionModal, this));
	},

	showNewVersionModal: function(event) {
		var name = $(event.srcElement).attr('data-name');
		console.log($(event.srcElement));
		// make ajax requests to get modal
		// /sites/{site_id}/{serv_id}/cheese_prism_modal
		var url = '/sites/' + Data.site_name + '/';
		url += Data.name_url + '/cheese_prism_modal';
		this.get('pull', url, {'name': name}, this.doneShowNewVersionModal);

		return false;
	},

	doneShowNewVersionModal: function(rslt) {
		$('#push-to-cheese-modal')
			.html(rslt)
			.modal();
	}
};

$(document).ready(function() {
	ServiceEnv.init();
});