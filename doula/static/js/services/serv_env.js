var ServiceEnv = {

	init: function() {
		_mixin(this, AJAXUtil);
		Data.init();

		this.bindToUIActions();
		this.bindToDataActions();
	},

	bindToUIActions: function() {
		$('a[rel="tooltip"]').tooltip({
			"delay": {
				"show": 500,
				"hide": 100
			}
		});

		$(".hide-on-load").each(function(index, el) {
			$(el).show();
		});

		$('.commit-accordion').on('show', function () {
			$(this).parent().removeClass('hidden').addClass('shown');
		});

		$('.commit-accordion').on('hide', function () {
			$(this).parent().removeClass('shown').addClass('hidden');
		});
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
			ServiceEnv.validateShowPushPackageModal();

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

	pushPackage: function(event) {
		if($(event.target).hasClass('disabled')) return false;

		var url = '/sites/' + Data.site_name + '/';
		url += Data.name_url + '/cheese_prism_push';

		var params = {
			'name': $('#push_package_name').val(),
			'branch': $('#push_package_branch').val(),
			'next_version': $('#push_package_version').val()
		};

		this.get('Releasing package to Cheese Prism', url, params, this.donePushPackage, this.failedPushPackage);
	},

	donePushPackage: function(rslt) {
		$('#push-to-cheese-modal').modal('hide');
		// alextodo make a call to update the queue
	},

	failedPushPackage: function(rslt) {
		$('#release_package_errors').removeClass('hide').html(rslt.html);
	}
};

$(document).ready(function() {
	ServiceEnv.init();
});