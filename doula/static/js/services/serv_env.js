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

		$('.new-version-btn').on('click', _bind(this.showPushPackageModal, this));
	},

	showPushPackageModal: function(event) {
		var name = $(event.srcElement).attr('data-name');

		// make ajax requests to get modal
		var url = '/sites/' + Data.site_name + '/';
		url += Data.name_url + '/cheese_prism_modal';

		this.get('pull', url, {'name': name}, this.doneShowPushPackageModal);

		return false;
	},

	doneShowPushPackageModal: function(rslt) {
		$('#push-to-cheese-modal').on('shown', function() {
			$('#push_package_branch')
				.on('change', ServiceEnv.validateShowPushPackageModal);
			$('#push_package_version')
				.on('keyup', ServiceEnv.validateShowPushPackageModal)
				.on('mouseup', ServiceEnv.validateShowPushPackageModal);

			$('#push_package').on('click', _bind(ServiceEnv.pushPackage, ServiceEnv));
		});

		$('#push-to-cheese-modal')
			.html(rslt)
			.modal();
	},

	// alextodo, what about checking against an existing package number?
	// have that happen on the backend
	validateShowPushPackageModal: function() {
		var branch = $.trim($('#push_package_branch').val());
		var version = $.trim($('#push_package_version').val());

		if (branch !== '' && version !== '') {
			$('#push_package').removeClass('disabled');
		}
		else {
			$('#push_package').addClass('disabled');
		}
	},

	// alextodo setup the eventing system that notifies us of things happening
	// on the backend. use the 10 lines of code for jquery events
	pushPackage: function() {
		var url = '/sites/' + Data.site_name + '/';
		url += Data.name_url + '/cheese_prism_push';

		var params = {
			'name': $('#push_package_name').val(),
			'branch': $('#push_package_branch').val(),
			'next_version': $('#push_package_version').val()
		};

		// alextodo, will need to properly handle errors from backend. show in modal
		this.get('Pushing package to Cheese Prism', url, params, this.donePushPackage, this.failedPushPackage);
	},

	donePushPackage: function(rslt) {
		console.log(rslt.job);
		$('#push-to-cheese-modal').modal('hide');
		// after this call make sure to update the UI, things need to be freezed
	},

	failedPushPackage: function(rslt) {
		// update the error messages in modal
		console.log('failed push package');
		console.log(rslt);

	}
};

$(document).ready(function() {
	ServiceEnv.init();
});