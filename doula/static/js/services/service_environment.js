var ServiceEnv = {

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

		$('#release-service').popover({placement: "bottom"});
		$('a.release').on('click', $.proxy(this.selectReleasePackages, this));
		$('select.package-select').
			on('change', $.proxy(this.updatePackageDropdownOnChange, this));

		// Queue stuff
		QueuedItems.subscribe(
			'queue-item-changed',
			$.proxy(this.queueItemChanged, this));
	},

	/***********************
	PACKAGE DROPDOWN RELATED
	************************/

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

			var html = (version) ?
				'New version <strong>' + version + '</strong>. ' :
				'Packaged will be removed. ';
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

	releaseService: function(event) {
		var releaseButton = $(event.target);
		var packages = this.getActiveReleasePackages();

		if(this.canRelease(releaseButton, packages)) {
			$('#release-service').popover('hide');

			this.disableReleaseServiceButton();

			var params = {packages: JSON.stringify(packages)};
			var url = '/sites/' + Data.site_name + '/' + Data.name_url + '/release';
			var msg = 'Releasing '+Data.name+' to '+Data.site_name+
					'. Please be patient and stay awesome.';
			this.post(url, params, this.doneReleaseService, this.failedReleaseService, msg);
		}
		else {
			if (releaseButton.hasClass('disabled')) {
				$('#release-service').popover('hide');
			}
			else {
				// No changes made. Show error message in popover
				setTimeout(function() {
					$('#release-service').popover('hide');
				}, 3500);
			}
		}

		event.preventDefault();

		return false;
	},

	canRelease: function(releaseButton, packages) {
		if (releaseButton.hasClass('disabled')) {
			return false;
		}

		return this.hasChanges(packages);
	},

	hasChanges: function(packages) {
		for(var name in packages) {
			return true;
		}

		return false;
	},

	disableReleaseServiceButton: function() {
		$('#release-service').addClass('disabled');
	},

	enableReleaseServiceButton: function() {
		$('#release-service').removeClass('disabled');
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

	cycle: function(event) {
		if (!$(event.target).hasClass('disabled')) {
			this.disableCycleButton();

			var url = '/sites/' + Data.site_name + '/' + Data.name_url + '/cycle';
			var msg = 'Cycling ' + Data.name + '. Please be patient and stay awesome.';
			this.get(url, {}, this.doneCycleService, false, msg);
		}

		event.preventDefault();

		return false;
	},

	doneCycleService: function(rslt) {
		// done
	},

	queueItemChanged: function(event, item) {
		// Cycle button gets enabled once
		if(item.job_type == 'cycle_services') {
			if(item.status == 'failed' || item.status == 'complete') {
				this.enableCycleButton();
			}
		}
		else if (item.job_type == 'push_to_cheeseprism') {
			if (item.status == 'complete') {
				this.updatePackagesDropdown(item.package_name, item.version);
			}
		}
	},

	disableCycleButton: function() {
		$('#cycle').addClass('disabled');
	},

	enableCycleButton: function() {
		$('#cycle').removeClass('disabled');
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

			$('#build_new_package_branch')
				.on('change click', ServiceEnv.validateShowPushPackageModal);
			$('#build_new_package_version')
				.on('keyup', ServiceEnv.validateShowPushPackageModal)
				.on('mouseup', ServiceEnv.validateShowPushPackageModal);

			$('#build_new_package').on('click', $.proxy(ServiceEnv.pushPackage, ServiceEnv));
		});

		$('#push-to-cheese-modal')
			.html(rslt)
			.modal();
	},

	// Validate the show push package version number and
	// update the next-full-version text
	validateShowPushPackageModal: function() {
		var branch = $.trim($('#build_new_package_branch').val());
		var version = $.trim($('#build_new_package_version').val());

		if (branch && version) $('#build_new_package').removeClass('disabled');
		else $('#build_new_package').addClass('disabled');

		var nextFullVersion = (version + '-' + branch).replace(/[\.-]$/, '');
		$('#next-full-version').html(nextFullVersion);
	},

	pushPackage: function(event) {
		if($(event.target).hasClass('disabled')) return false;

		var url = '/sites/' + Data.site_name + '/';
		url += Data.name_url + '/cheese_prism_push';

		var params = {
			'name': $('#build_new_package_name').val(),
			'branch': $('#build_new_package_branch').val(),
			'next_version': $('#build_new_package_version').val()
		};

		var msg = 'Pushing package '+params.name+' version '+
				params.next_version + '. Please be patient and stay awesome.';

		this.get(url, params, this.donePushPackage, this.failedPushPackage, msg);

		return false;
	},

	donePushPackage: function(rslt) {
		$('#push-to-cheese-modal').modal('hide');
	},

	updatePackagesDropdown: function(package_name, version) {
		$('#pckg_select_dummycode').
			append('<option value="' + version + '">' + version + '</option>').
			val(version).
			change();
	},

	failedPushPackage: function(rslt) {
		$('#release_package_errors').removeClass('hide').html(rslt.html);
	}
};

$(document).ready(function() {
	ServiceEnv.init();
});