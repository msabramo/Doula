var ServiceEnv = {

    /****************
    INITIAL SERVICE
    *****************/

    init: function() {
        this.releases = __releases;
        this.other_packages = __other_packages;
        this.latest_service_config = __latest_service_config;
        this.service = __service;

        _mixin(this, AJAXUtil);
        _mixin(this, Packages);

        this.showElementsHiddenOnLoad();
        this.bindToUIActions();
        this.bindToDataActions();
        this.initPackagesAsMixin(this.service.site_name, this.service.name_url);
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

    /**********************
    UI Actions
    ***********************/

    bindToUIActions: function() {
        this.addVersionMessageBelowPackageSelects();
        this.bindToReleasesAndPackages();
        this.bindToServiceConfigChanges();

        // Dropdown for add python package
        this.bindToAddPythonPackageSelects();

        // Queue stuff
        QueueView.subscribe(
            'queue-item-changed',
            $.proxy(this.queueServiceJobChanged, this));

        // Handle the mini
        this.bindToMiniDashboardActions();
    },

    bindToServiceConfigChanges: function() {
        $('#config_sha').on('change blur', $.proxy(this.updateServiceConfigMessage, this));
        // Always select the latest config onload. Then call onchange.
        $('#config_sha').val(this.latest_service_config.sha).change();
    },

    bindToReleasesAndPackages: function() {
        $('#release-service-locked')._on('click', function() {});
        $('a.release')._on('click', this.selectReleaseConfigAndPackages, this);

        $('select.package-select').
            on('change', $.proxy(this.updatePackageDropdownOnChange, this));
    },

    bindToAddPythonPackageSelects: function() {
        $('#pckg_select_add_new_package')._on('change',
                                               this.updateAddNewPackageVersions,
                                               this,
                                               allowEventToBubble=true);

        var addNewPackageSelects = $('#pckg_select_add_new_package, #pckg_select_add_new_package_version');
        addNewPackageSelects._on('change', this.updateAddNewPackageVersionsMessage, this);
        addNewPackageSelects._on('change', this.updateAfterSelectAddNewPackageVersion, this);
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
        var url = '/sites/' + this.service.site_name + '/' + this.service.name_url + '/dash';
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
    Service Config dropdown
    *************************************/

    updateServiceConfigMessage: function(event) {
        var activeSha = $('#config_sha').val();
        var sc = this.findServiceConfigBySha(activeSha); // Selected Config
        var ac = this.service.config; // Active Config
        var lc = this.latest_service_config; // Latest Config

        // If the selected, active and latest configs agree we show no warning. otherwise warn
        var warnClass = (sc.sha == ac.sha && sc.sha == lc.sha) ? '' : 'warning';

        $('#config_sha').removeClass('warning').addClass(warnClass);

        var warnHTML = this.buildServiceConfigWarnHTML(sc, ac, lc);
        $('#config_sha_warning').html(warnHTML).removeClass('warning').addClass(warnClass);

        var html = this.buildServiceConfigColHTML(sc);
        $('#service_config_col').html(html).removeClass('warning').addClass(warnClass);
    },

    buildServiceConfigColHTML: function(sc) {
        var html = "<a href=\"http://code.corp.surveymonkey.com/config/";
        html += sc.service + "/tree/" + sc.sha + "\" target=\"_blank\">";
        html += sc.message + "</a>";

        return html;
    },

    buildServiceConfigWarnHTML: function(sc, ac, lc) {
        var html = "";

        if (sc.sha == ac.sha && sc.sha == lc.sha) {
            // This is the only situation that does not appear as a warning
            html = "The selected config from <strong>" + sc.formatted_date +
                "</strong> is the latest and active version.";
        }
        else if (sc.sha != ac.sha && sc.sha == lc.sha) {
            // the selected config is not the active config, but it is the latest
            html = "The selected and latest config from <strong>" + sc.formatted_date +
                    "</strong> is <strong>NOT</strong> the active config. <br /><br />";
            html += "The active config is from <strong>" + ac.formatted_date + "</strong>.";
        }
        else if (sc.sha == ac.sha && sc.sha != lc.sha) {
            // the selected and active config is NOT the latest
            html = "The selected and active config from <strong>" + sc.formatted_date +
                    "</strong> is <strong>NOT</strong> the latest version. <br /><br />";
            html += "The latest config is from <strong>" + lc.formatted_date + "</strong>.";
        }
        else if (sc.sha != ac.sha && sc.sha != lc.sha) {
            // the selected config is neither the latest nor the latest
            html = "The selected config from <strong>" + sc.formatted_date +
                    "</strong> is <strong>NOT</strong> the latest version. <br /><br />";
            html += "The latest config is from <strong>" + lc.formatted_date + "</strong>.";
        }

        return html;
    },

    findServiceConfigBySha: function(sha) {
        for (var i = 0; i < __service_configs.length; i++) {
            if (__service_configs[i].sha == sha) return __service_configs[i];
        }

        return {};
    },

    isConfigUpToDate: function() {
        return (this.latest_service_config.sha == this.service.config.sha);
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
    selectReleaseConfigAndPackages: function(event, dropdownLink) {
        this.seleectReleaseConfig(dropdownLink);
        this.selectReleasePackageFromDropdown(dropdownLink);
        this.showDiffForRelease(dropdownLink);
    },

    seleectReleaseConfig: function(dropdownLink) {
        var releaseDate = dropdownLink.attr('data-date');
        var release = this.findReleaseByDate(releaseDate);

        $('#config_sha').val(release.sha1_etc).change();
    },

    showDiffForRelease: function(dropdownLink) {
        var params = this.getDiffForReleaseParams(dropdownLink);
        var url = '/sites/' + this.service.site_name + '/' + this.service.name_url + '/diff';
        var msg = 'Pulling release diff. Please be patient and stay awesome.';

        this.post(url, params, this.doneShowDiffForRelease, null, msg);
    },

    /**
    * Get all the parameters needed to build a release on the fly
    * (sha for the etc and all the packages)
    */
    getDiffForReleaseParams: function(dropdownLink) {
        var date = '';

        if (typeof(dropdownLink) != 'undefined') {
            date = dropdownLink.data('date');
        };

        return {
            date: date,
            sha: $('#config_sha').val(),
            packages: JSON.stringify(this.getActiveReleasePackages(true))
        };
    },

    doneShowDiffForRelease: function(rslt) {
        this.doneUpdateMiniDashboard(rslt);

        if (rslt.diff.diff_exists && !this.isJobsDetailViewVisible()) {
            this.showDashboardDetailView('releases');
        }
    },

    isJobsDetailViewVisible: function() {
        return $('#mini-dashboard-detail-jobs').is(':visible');
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
        this.showDiffForRelease();
    },

    updatePackageDropdown: function(name, version) {
        // Only proceed if the select has the value
        if (this.selectHasValue(name, version)) {
            var select = $('#pckg_select_' + name);
            select.val(version);

            var message = $('#pckg_select_msg_' + name);
            var originalVal = $.trim(select.attr('data-original-val'));

            if(originalVal != version && originalVal != 'undefined') {
                select.addClass('warning');
                message.addClass('warning');

                var html = (version) ?
                    'New version <strong>' + version + '</strong>. ' :
                    'Packaged will be removed. ';
                html += 'Current version <strong>' + originalVal + '</strong>.';
                message.html(html);
            }
            else {
                select.removeClass('warning');
                message.removeClass('warning');
                message.html('Current version <strong>' + originalVal + '</strong>.');
            }
        }
    },

    selectHasValue: function(name, value) {
        return $("#pckg_select_" + name + " option[value='"+ value + "']").length !== 0;
    },

    makeReleaseLinkActive: function(el) {
        $('#release-dropdown li').each(function(i, li) {
            $(li).removeClass('active');
        });

        el.closest('li').addClass('active');
    },

    /****************************
    Add Python Package Functions
    *****************************/

    /**
    * Update the version number according to the version
    */
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

    /*
    * Update the diff UI after a user selects a new package to add to python
    */
    updateAfterSelectAddNewPackageVersion: function() {
        this.showDiffForRelease();
    },

    /**
    * Update the message
    */
    updateAddNewPackageVersionsMessage: function() {
        var packageName = $('#pckg_select_add_new_package').val();
        var version = $('#pckg_select_add_new_package_version').val();
        var msg = '';

        if (packageName && version) {
            var name = this.other_packages[packageName].name;
            msg = 'New version <strong>' + name + version + '</strong>. No current version exists.';
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
        if (!$('#release-service').prop('disabled')) {
            this.disableReleaseServiceButton();

            var params = {
                sha: $('#config_sha').val(),
                packages: JSON.stringify(this.getActiveReleasePackages())
            };
            var url = '/sites/' + this.service.site_name + '/' + this.service.name_url + '/release';
            var msg = 'Releasing '+this.service.name+' to '+this.service.site_name+
                    '. Please be patient and stay awesome.';
            this.post(url, params, this.doneReleaseService, this.failedReleaseService, msg);
        }
    },

    getActiveReleasePackages: function(returnAllPackages) {
        var packages = {};
        returnAllPackages = returnAllPackages || false;

        $('select.package-select').each(function(i, select) {
            select = $(select);
            // Releases need the actual name on cheese prism
            // not the comparable name.
            var name = select.data('name');
            var version = select.val();
            var originalVal = $.trim(select.attr('data-original-val'));

            if ((originalVal != version && typeof(name) != 'undefined') ||
                (returnAllPackages && typeof(name) != 'undefined')) {
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
        $('#release-service').prop('disabled', true).addClass('disabled');
    },

    enableReleaseServiceButton: function() {
        setTimeout(function() {
            $('#release-service').prop('disabled', false).removeClass('disabled');
        }, 4000);
    },

    updateServiceAfterRelease: function(job) {
        this.service.config.sha = job.manifest.sha1_etc;
        this.updateServiceConfigMessage();
        this.updateServicePackagesAfterRelease(job);
        this.updateMiniDashboard();
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
            this.service.packages[comparable_name]['version'] = version;
        }
    },

    /****************
    CYCLE SERVICE
    *****************/

    cycle: function(event, button) {
        if (!button.hasClass('disabled')) {
            this.disableCycleButton();

            var url = '/sites/' + this.service.site_name + '/' + this.service.name_url + '/cycle';
            var msg = 'Cycling ' + this.service.name + '. Please be patient and stay awesome.';
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
        if (job.job_type == 'cycle_service') {
            if(job.status == 'failed' || job.status == 'complete') {
                this.enableCycleButton();
                this.updateMiniDashboard();
                this.showDiffForRelease();
            }
        }
        else if (job.job_type == 'release_service') {
            if (job.status == 'failed' || job.status == 'complete') {
                this.updateMiniDashboard();
            }

            if (job.status == 'complete') {
                this.updateServiceAfterRelease(job);
            }
        }
        else if (job.job_type == 'build_new_package') {
            if (job.status == 'complete') {
                this.showDashboardDetailView();
            }
        }
    }
};

$(document).ready(function() {
    ServiceEnv.init();
});