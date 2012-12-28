var Packages = {

    siteName: '',
    serviceName: '',

    /**
    *   This init used when Packages object is used as a standalone object
    *   instead of a mixin.
    */
    init: function() {
        _mixin(this, AJAXUtil);

        this.setupTooltips();
        this.bindToBuildNewPackageButtons();
    },

    setupTooltips: function() {
        $('a[rel="tooltip"]').tooltip({
            "delay": {
                "show": 500,
                "hide": 100
            }
        });
    },

    // This object is used as a mixin by service_environment.js
    // so we give it a special init that ensures all the data is
    // required by packages exist.
    initPackagesAsMixin: function(siteName, serviceName) {
        this.siteName = siteName;
        this.serviceName = serviceName;

        this.bindToBuildNewPackageButtons();
    },

    bindToBuildNewPackageButtons: function() {
        $('.new-version-btn').on('click', $.proxy(this.showBuildNewPackageModal, this));

        // Queue stuff
        QueueView.subscribe(
            'queue-item-changed',
            $.proxy(this.queuePackageJobChanged, this));
    },

    /****************
    PUSH PACKAGE
    *****************/

    // Make ajax call to get build new package modal HTML
    showBuildNewPackageModal: function(event) {
        var name = $(event.target).data('name');
        var url = '/packages/build_new_package_modal';
        this.get(url, {'name': name}, this.doneShowBuildNewPackageModal);

        return false;
    },

    doneShowBuildNewPackageModal: function(rslt) {
        $('#build-new-package-modal').on('shown', $.proxy(function() {
            this.validateShowBuildNewPackageModal();

            $('#build_new_package_branch')
                .on('change click', this.validateShowBuildNewPackageModal);
            $('#build_new_package_version')
                .on('keyup', this.validateShowBuildNewPackageModal)
                .on('mouseup', this.validateShowBuildNewPackageModal);

            $('#build_new_package').on('click', $.proxy(this.buildNewPackage, this));
        }, this));

        $('#build-new-package-modal').html(rslt).removeClass('hide').modal();
    },

    // Validate the show push package version number and
    // update the next-full-version text
    validateShowBuildNewPackageModal: function() {
        var branch = $.trim($('#build_new_package_branch').val());
        var version = $.trim($('#build_new_package_version').val());

        if (branch && version) $('#build_new_package').removeClass('disabled');
        else $('#build_new_package').addClass('disabled');

        var nextFullVersion = (version + '-' + branch).replace(/[\.-]$/, '');
        $('#next-full-version').html(nextFullVersion);
    },

    /**
    *   Send the build new package request to queue
    */
    buildNewPackage: function(event) {
        // Check that the push isn't disabled
        if(!$(event.target).hasClass('disabled')) {
            var url = '/packages/build_new_package';
            var params = {
                'site_name': this.siteName,
                'service_name': this.serviceName,
                'name': $('#build_new_package_name').val(),
                'branch': $('#build_new_package_branch').val(),
                'next_version': $('#build_new_package_version').val()
            };
            var msg = 'Pushing package '+params.name+' version '+
                    params.next_version + '. Please be patient and stay awesome.';

            this.get(url, params, this.doneBuildNewPackage, this.failedBuildNewPackage, msg);
        }

        return false;
    },

    doneBuildNewPackage: function(rslt) {
        $('#build-new-package-modal').modal('hide');

        // If the ServiceEnv exist then show this
        if (ServiceEnv) ServiceEnv.showDashboardDetailView();
    },

    failedBuildNewPackage: function(rslt) {
        $('#build_package_errors').removeClass('hide').html(rslt.html);
    },

    /****************
    Queue Item Changes
    *****************/

    queuePackageJobChanged: function(event, job) {
        if (job.job_type == 'build_new_package') {
            if (job.status == 'complete') {
                this.updatePackagesDropdown(job);

                // If the ServiceEnv exist then show this
                if (ServiceEnv) ServiceEnv.showDashboardDetailView();
            }
        }
    },

    /**
    *   After a package is built, automatically choose it for the user
    */
    updatePackagesDropdown: function(job) {
        $('#pckg_select_' + job.comparable_name).
            prepend('<option value="' + job.version + '">' + job.version + '</option>').
            val(job.version).
            change();
    }
};

$(document).ready(function() {
    // Run automatically on the packages URL
    if (document.location.href.match(/\/packages/)) {
        Packages.init();
    }
});

