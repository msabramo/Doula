var ServiceEnv = {

	cycleServiceJobs: [],

	/****************
	INITIAL SERVICE
	*****************/

	init: function() {
		this.releases = __releases;

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

		// Dropdown packages

		this.addOriginalVersionToPackageSelects();

		$('a.release').on('click', $.proxy(this.selectReleasePackages, this));
		$('select.package-select').
			on('change', $.proxy(this.updatePackageDropdownOnChange, this));

		// Queue stuff
		QueuedItems.subscribe(
			'queue-item-changed',
			$.proxy(this.queueItemChanged, this));
	},

	/*******************
	PACKAGE DROPDOWN RELATED
	********************/

	addOriginalVersionToPackageSelects: function() {
		$('.package-select').each(function(i, select) {
			select = $(select);
			select.attr('data-original-val', select.val());

			var safeID = select.attr('id').
				replace('pckg_select_', '').
				replace('.', '\\.');
			$('#pckg_select_msg_' + safeID).
				html('Current version <strong>' + select.val() + '</strong>.');
		});
	},

	selectReleasePackages: function(event) {
		var target = $(event.target);
		this.makeReleaseLinkActive(target);

		var releaseDate = target.attr('data-date');
		var release = this.findReleaseByDate(releaseDate);

		for(i=0; i < release.packages.length; i++) {
			var pckg = release.packages[i];

			var safeID = pckg.name.toLowerCase().replace('.', '\\.');
			this.updatePackageDropdown(safeID, pckg.version);
		}

		// Close the button dropdown menu
		target.closest('div.btn-group').removeClass('open');

		return false;
	},

	findReleaseByDate: function(releaseDate) {
		var release;

		for(var i = 0; i < this.releases.length; i++) {
			if(this.releases[i].date == releaseDate) {
				return this.releases[i];
			}
		}

		return false;
	},

	updatePackageDropdownOnChange: function(event) {
		var target = $(event.target);
		var name = target.attr('id').replace('pckg_select_', '');

		this.updatePackageDropdown(name, target.val());
	},

	updatePackageDropdown: function(name, version) {
		var safeID = name.toLowerCase().replace('.', '\\.');
		var select = $('#pckg_select_' + safeID);
		var message = $('#pckg_select_msg_' + safeID);
		var originalVal = $.trim(select.attr('data-original-val'));

		if(originalVal != version && originalVal != 'undefined') {
			select.val(version);
			select.addClass('warning');
			message.addClass('warning');

			var html = 'New version <strong>' + version + '</strong>. ';
			html += 'Current version <strong>' + originalVal + '</strong>.';
			message.html(html);
		}
		else {
			select.val(version);
			select.removeClass('warning');
			message.removeClass('warning');
			message.html('Current version <strong>' + originalVal + '</strong>.');
		}
	},

	makeReleaseLinkActive: function(el) {
		$('#release-dropdown li').each(function(i, li) {
			$(li).removeClass('active');
		});

		el.parent().addClass('active');
	},

	/*******************
	DATA ACTIONS
	********************/

	bindToDataActions: function() {
		$('#add-pckg').on('click', function() {
			// show modal dialog of packages available on cheese prism
			// that are not on here
			$('#add-packages').modal();
		});

		$('#cycle').on('click', $.proxy(this.cycle, this));
		$('.new-version-btn').on('click', $.proxy(this.showPushPackageModal, this));

		$('#release-service').on('click', $.proxy(this.releaseService, this));
	},

	/****************
	RELEASE SERVICE
	*****************/

	releaseService: function() {
		var packages = this.getActiveReleasePackages();

		if(this.hasChanges(packages)) {
			this.disableReleaseServiceButton();

			var params = {packages: JSON.stringify(packages)};
			var url = '/sites/' + Data.site_name + '/' + Data.name_url + '/release';
			this.post(url, params, this.doneReleaseService, this.failedReleaseService);
		}

		return false;
	},

	hasChanges: function(packages) {
		for(var name in packages) {
			return true;
		}

		return false;
	},

	disableReleaseServiceButton: function() {
		this.disableButton('release-service');
	},

	enableReleaseServiceButton: function() {
		this.enableButton('release-service', this.releaseService);
	},

	getActiveReleasePackages: function() {
		var packages = {};

		$('select.package-select').each(function(i, select) {
			select = $(select);
			var name = select.attr('id').replace('pckg_select_', '');
			var version = select.val();
			var originalVal = $.trim(select.attr('data-original-val'));

			if(originalVal != version && originalVal != 'undefined') {
				packages[name] = version;
			}
		});

		return packages;
	},

	doneReleaseService: function(rslt) {
		this.enableReleaseServiceButton();
	},

	failedReleaseService: function(rslt) {
		this.enableReleaseServiceButton();
		this._showStandardErrorMessage(rslt);
	},

	/****************
	CYCLE SERVICE
	*****************/

	// alextodo, last thing to do is initially allow us to cycle the services
	// disable the button if there is currently someone trying to cycle this service
	// does this query for everyone else too?
	cycle: function(event) {
		this.disableCycleButton();

		var url = '/sites/' + Data.site_name + '/' + Data.name_url + '/cycle';
		this.get(url, {}, this.doneCycleService);

		return false;
	},

	// This here would have to listen for the pass or failure of the pen
	// would be nice to be notified of an event
	doneCycleService: function(rslt) {
		this.cycleServiceJobs.push(rslt.job_id);
	},

	queueItemChanged: function(event, item) {
		// Cycle button gets enabled once
		if(item.job_type == 'cycle_services') {
			if(item.status == 'failed' || item.status == 'complete') {
				this.cycleServiceJobs = _withoutArray(this.cycleServiceJobs, item.id, 'id');

				if(this.cycleServiceJobs.length === 0) this.enableCycleButton();
			}
		}
	},

	disableCycleButton: function() {
		this.disableButton('cycle');
	},

	enableCycleButton: function() {
		this.enableButton('cycle', this.cycle);
	},

	/****************
	COMMON
	*****************/

	disableButton: function(id) {
		$('#'+id)
			.unbind()
			.addClass('disabled')
			.bind('click', function() { return false; });
	},

	enableButton: function(id, func) {
		$('#'+id)
			.removeClass('disabled')
			.on('click', $.proxy(func, this));
	},

	/****************
	PUSH PACKAGE
	*****************/

	showPushPackageModal: function(event) {
		var name = $(event.srcElement).attr('data-name');

		// make ajax requests to get modal
		var url = '/sites/' + Data.site_name + '/';
		url += Data.name_url + '/cheese_prism_modal';

		this.get(url, {'name': name}, this.doneShowPushPackageModal);

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

			$('#push_package').on('click', $.proxy(ServiceEnv.pushPackage, ServiceEnv));
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

		this.get(url, params, this.donePushPackage, this.failedPushPackage);
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