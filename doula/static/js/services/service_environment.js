var ServiceEnv = {

    /****************
    INITIAL SERVICE
    *****************/

    init: function() {
        this.releases = __releases;

        _mixin(this, AJAXUtil);
        _mixin(this, Packages);

        Data.init();

        this.bindToUIActions();
        this.bindToDataActions();
        this.initPackagesAsMixin(Data.site_name, Data.name_url);
    },

    bindToUIActions: function() {
        $('a[rel="tooltip"]').tooltip({
            "delay": {
                "show": 500,
                "hide": 100
            }
        });

        // Hide elements marked as hide on load, makes page load smoother
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
        this.addVersionMessageBelowPackageSelects();

        $('a.release').on('click', $.proxy(this.selectReleasePackages, this));
        $('select.package-select').
            on('change', $.proxy(this.updatePackageDropdownOnChange, this));

        // Queue stuff
        QueueView.subscribe(
            'queue-item-changed',
            $.proxy(this.queueItemChanged, this));

        // Handle the mini
        this.bindToMiniDashboardActions();
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
    showRecentJobsDetailView: function() {
        this.miniDashboardDetailElements.addClass('hide');
        $('#mini-dashboard-detail-jobs').removeClass('hide');

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

            var packageName = select.attr('id').replace('pckg_select_', '');

            $('#pckg_select_msg_' + packageName).
                html('Current version <strong>' + select.val() + '</strong>.');
        });
    },

    selectReleasePackages: function(event) {
        var target = $(event.target);
        this.makeReleaseLinkActive(target);

        var releaseDate = target.attr('data-date');
        var release = this.findReleaseByDate(releaseDate);

        console.log('selectReleasePackages: make sure this has a comparable name. each package needs it.');
        console.log(release.packages);

        for(i=0; i < release.packages.length; i++) {
            var pckg = release.packages[i];
            console.log('found a package. lets make usre it has comparable');
            console.log(pckg);

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

    /*******************
    DATA ACTIONS
    ********************/

    bindToDataActions: function() {
        $('#cycle').on('click', $.proxy(this.cycle, this));
        $('#release-service').on('click', $.proxy(this.releaseService, this));
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

        event.preventDefault();

        return false;
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
        this.showRecentJobsDetailView();
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
        this.showRecentJobsDetailView();
    },

    disableCycleButton: function() {
        $('#cycle').addClass('disabled');
    },

    enableCycleButton: function() {
        $('#cycle').removeClass('disabled');
    },

    /****************
    Queue Item Changes
    *****************/

    queueItemChanged: function(event, item) {
        // Cycle button gets enabled once
        if(item.job_type == 'cycle_service') {
            if(item.status == 'failed' || item.status == 'complete') {
                this.enableCycleButton();
                this.updateMiniDashboard();
            }
        }
        else if (item.job_type == 'build_new_package') {
            if (item.status == 'complete') {
                // alextodo. need to put this in the updatePackageDropdwon
                // in package.js
                this.updatePackagesDropdown(item.package_name, item.version);
            }
        }
        else if (item.job_type == 'release_service') {
            if(item.status == 'failed' || item.status == 'complete') {
                this.updateMiniDashboard();
            }
        }
    },

    /**
    *   After a package is built, automatically choose it for the user
    */
    updatePackagesDropdown: function(package_name, version) {
        $('#pckg_select_' + package_name).
            prepend('<option value="' + version + '">' + version + '</option>').
            val(version).
            change();
    }
};

$(document).ready(function() {
    ServiceEnv.init();
});