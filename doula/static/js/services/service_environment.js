var ServiceEnv = {

    /****************
    INITIAL SERVICE
    *****************/

    init: function() {
        this.releases = __releases;
        this.other_packages = __other_packages;

        _mixin(this, AJAXUtil);
        _mixin(this, Packages);

        Data.init();

        this.bindToUIActions();
        this.bindToDataActions();
        this.initPackagesAsMixin(Data.site_name, Data.name_url);
    },

    bindToUIActions: function() {
        this.initToolTips();
        this.showElementsHiddenOnLoad();

        this.addVersionMessageBelowPackageSelects();
        this.bindToReleasesAndPackages();
        // Dropdown for add python package
        this.bindToAddPythonPackageSelects();

        // Queue stuff
        QueueView.subscribe(
            'queue-item-changed',
            $.proxy(this.queueServiceJobChanged, this));

        // Handle the mini
        this.bindToMiniDashboardActions();
    },

    initToolTips: function() {
        $('a[rel="tooltip"]').tooltip({
            "delay": {
                "show": 500,
                "hide": 100
            }
        });
    },

    // Hide elements marked as hide on load, makes page load smoother
    showElementsHiddenOnLoad: function() {
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

    bindToReleasesAndPackages: function() {
        $('a.release')._on('click', this.selectReleasePackages, this);

        $('select.package-select').
            on('change', $.proxy(this.updatePackageDropdownOnChange, this));
    },

    bindToAddPythonPackageSelects: function() {
        $('#pckg_select_add_new_package').on('change',
            $.proxy(this.updateAddNewPackageVersions, this));

        $('#pckg_select_add_new_package, #pckg_select_add_new_package_version').on('change',
            $.proxy(this.updateAddNewPackageVersionsMessage, this));
    },

    /*********************
    Handle Mini Dashboard
    **********************/

    firstRun: true,
    miniDashboardDetails: $('.mini-dashboard-details'),
    miniDashboardDetailElements: $('.mini-dashboard-detail'),

    bindToMiniDashboardActions: function() {
        if (this.firstRun) {
            this.firstRun = false;

            // The first time around everything is hidden
            this.miniDashboardDetails.slideUp('fast');
            this.miniDashboardDetailElements.addClass('hide');
        }

        $('.mini-dashboard-square').unbind();

        $('.mini-dashboard-square').on('click', $.proxy(function(event) {
            var targetDetail = $($(event.target).
                                    closest('div.mini-dashboard-square').
                                    data('target'));

            // This target is visible and got clicked. Hide everything
            if (targetDetail.is(":visible")) {
                this.miniDashboardDetails.slideUp('fast');
                this.miniDashboardDetailElements.addClass('hide');
            }
            // Another box got clicked while open. Show the target element
            else if (this.miniDashboardDetails.is(":visible")) {
                this.miniDashboardDetailElements.addClass('hide');
                targetDetail.removeClass('hide');
            }
            // If everything is hidden. Slide down the box and show dashboard details
            // and show the detail for the specific target
            else if (!this.miniDashboardDetails.is(":visible")) {
                this.miniDashboardDetailElements.addClass('hide');
                targetDetail.removeClass('hide');

                this.miniDashboardDetails.slideDown('fast');
            }
        }, this));
    },

    // After any job action open up the recent jobs view
    // viewType can be either (jobs|config|releases). Default is jobs.
    showDashboardDetailView: function(viewType) {
        viewType = viewType || 'jobs';

        this.miniDashboardDetailElements.addClass('hide');
        $('#mini-dashboard-detail-' + viewType).removeClass('hide');

        this.miniDashboardDetails.slideDown('fast');
    },

    // Update the mini dashboard after a change

    updateMiniDashboard: function() {
        var url = '/sites/' + Data.site_name + '/' + Data.name_url + '/dash';
        this.get(url, {}, this.doneUpdateMiniDashboard, false, msg=false);
    },

    doneUpdateMiniDashboard: function(rslt) {
        // Update the squares, the config and the releases details
        $('#mini-dashboard-squares').replaceWith(rslt.squaresHTML);
        $('#mini-dashboard-detail-config').replaceWith(rslt.configHTML);
        $('#mini-dashboard-detail-releases').replaceWith(rslt.releasesHTML);

        // Reset the cached jquery elements
        this.miniDashboardDetails = $('.mini-dashboard-details');
        this.miniDashboardDetailElements = $('.mini-dashboard-detail');

        this.bindToMiniDashboardActions();
    },

    /************************************
    Package dropdowns for Release Service
    *************************************/

    addVersionMessageBelowPackageSelects: function() {
        $('.package-select').each(function(i, select) {
            select = $(select);
            select.attr('data-original-val', select.val());

            var packageName = select.data('comparable-name');

            $('#pckg_select_msg_' + packageName).
                html('Current version <strong>' + select.val() + '</strong>.');
        });
    },

    /**
    * Select the release from the drop down. Update the drop downs and
    * show the release diff in the dashboard
    *
    */
    selectReleasePackages: function(event, dropdownLink) {
        console.log('hello there');
        console.log(event.target);

        this.showDiffForRelease(dropdownLink);
        this.selectReleasePackageFromDropdown(dropdownLink);
    },

    showDiffForRelease: function(dropdownLink) {
        var params = {date: dropdownLink.data('date')};
        var url = '/sites/' + Data.site_name + '/' + Data.name_url + '/diff';
        var msg = 'Pulling release diff. Please be patient and stay awesome.';

        this.post(url, params, this.doneShowDiffForRelease, null, msg);
    },

    doneShowDiffForRelease: function(rslt) {
        console.log('hello there rslt');
        console.log(rslt);

        this.doneUpdateMiniDashboard(rslt);
        this.showDashboardDetailView('releases');
    },

    selectReleasePackageFromDropdown: function(dropdownLink) {
        this.makeReleaseLinkActive(dropdownLink);

        var releaseDate = dropdownLink.attr('data-date');
        var release = this.findReleaseByDate(releaseDate);

        if (release) {
            // Roll through this services dropdowns and select the changed
            // package version numbers
            for(i=0; i < release.packages.length; i++) {
                var pckg = release.packages[i];
                this.updatePackageDropdown(pckg.comparable_name, pckg.version);
            }
        }

        // Close the button dropdown menu
        dropdownLink.closest('div.btn-group').removeClass('open');
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
        var selectEl = $(event.target);
        var name = selectEl.data('comparable-name');
        var value = selectEl.val();

        this.updatePackageDropdown(name, value);
    },

    updatePackageDropdown: function(name, version) {
        var select = $('#pckg_select_' + name);
        var message = $('#pckg_select_msg_' + name);
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

    updateAddNewPackageVersions: function() {
        var value = $('#pckg_select_add_new_package').val();

        // Update the versions drop down
        if (value) {
            var options = "<option value=\"\">Select a Version</option>";
            var versions = this.other_packages[value].versions;

            for (var i = 0; i < versions.length; i++) {
                options += "<option value=\"" + versions[i] + "\">";
                options += versions[i] + "</option>";
            }

            $('#pckg_select_add_new_package_version').html(options);
        }
    },

    updateAddNewPackageVersionsMessage: function() {
        var packageName = $('#pckg_select_add_new_package').val();
        var version = $('#pckg_select_add_new_package_version').val();
        var msg = '';

        if (packageName && version) {
            var name = this.other_packages[packageName].name;
            msg = 'Adding package <strong>' + name + '</strong> ';
            msg += 'version <strong>' + version + '</strong>.';
        }

        $('#pckg_select_add_new_package_msg').html(msg);
    },

    /*******************
    DATA ACTIONS
    ********************/

    bindToDataActions: function() {
        $('#cycle')._on('click', this.cycle, this);
        $('#release-service')._on('click', this.releaseService, this);
    },

    /****************
    RELEASE SERVICE
    *****************/

    releaseService: function(event) {
        this.disableReleaseServiceButton();

        var params = {
            packages: JSON.stringify(this.getActiveReleasePackages())
        };
        var url = '/sites/' + Data.site_name + '/' + Data.name_url + '/release';
        var msg = 'Releasing '+Data.name+' to '+Data.site_name+
                '. Please be patient and stay awesome.';
        this.post(url, params, this.doneReleaseService, this.failedReleaseService, msg);
    },

    getActiveReleasePackages: function() {
        var packages = {};

        $('select.package-select').each(function(i, select) {
            select = $(select);
            // Releases need the actual name on cheese prism
            // not the comparable name.
            var name = select.data('name');
            var version = select.val();
            var originalVal = $.trim(select.attr('data-original-val'));

            if (originalVal != version && originalVal != 'undefined') {
                packages[name] = version;
            }
        });

        // Check if the user is adding a new package as well
        // Add that new package to this service
        var packageName = $('#pckg_select_add_new_package').val();
        var version = $('#pckg_select_add_new_package_version').val();

        if (packageName && version) {
            packages[this.other_packages[packageName].name] = version;
        }

        return packages;
    },

    doneReleaseService: function(rslt) {
        this.showDashboardDetailView();
        this.enableReleaseServiceButton();
    },

    failedReleaseService: function(rslt) {
        this.enableReleaseServiceButton();
        this._showStandardErrorMessage(rslt);
    },

    disableReleaseServiceButton: function() {
        $('#release-service').addClass('disabled');
    },

    enableReleaseServiceButton: function() {
        $('#release-service').removeClass('disabled');
    },

    // Update the current service and drop downs
    updateServicePackagesAfterRelease: function(job) {
        for (var comparable_name in job.manifest.comparable_packages) {
            var select = $('#pckg_select_' + comparable_name);
            var version = job.manifest.comparable_packages[comparable_name];

            // Set the drop down's new default value. reset message
            // by calling the change event
            select.attr('data-original-val', version);
            select.change();

            // Update the data attribute value for the version
            Data.packages[comparable_name]['version'] = version;
        }
    },

    /****************
    CYCLE SERVICE
    *****************/

    cycle: function(event, button) {
        if (!button.hasClass('disabled')) {
            this.disableCycleButton();

            var url = '/sites/' + Data.site_name + '/' + Data.name_url + '/cycle';
            var msg = 'Cycling ' + Data.name + '. Please be patient and stay awesome.';
            this.get(url, {}, this.doneCycleService, false, msg);
        }
    },

    doneCycleService: function(rslt) {
        this.showDashboardDetailView();
    },

    disableCycleButton: function() {
        $('#cycle').addClass('disabled');
    },

    enableCycleButton: function() {
        $('#cycle').removeClass('disabled');
    },

    /****************
    Queue Job Changes
    *****************/

    queueServiceJobChanged: function(event, job) {
        // Cycle button gets enabled once
        if (job.job_type == 'cycle_service') {
            if(job.status == 'failed' || job.status == 'complete') {
                this.enableCycleButton();
                this.updateMiniDashboard();
            }
        }
        else if (job.job_type == 'release_service') {
            if (job.status == 'failed' || job.status == 'complete') {
                this.updateMiniDashboard();
            }

            if (job.status == 'complete') {
                this.updateServicePackagesAfterRelease(job);
            }
        }
    }
};

$(document).ready(function() {
    ServiceEnv.init();
});