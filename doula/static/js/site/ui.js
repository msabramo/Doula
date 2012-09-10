var UI = {

    statusClassHash: {
        'deployed'                : 'deployed',
        'uncommitted_changes'      : 'error',
        'change_to_config'         : 'changed',
        'change_to_app_env'        : 'changed',
        'change_to_app_and_config' : 'changed',
        'tagged'                   : 'tagged'
    },

    init: function() {
        this.showTooltips();

        $('.collapse').collapse({
            parent: '#sites-accordion',
            toggle: false
        });
    },

    showTooltips: function() {
        $('a[rel="tooltip"]').on('click', function(event, a) {
            if ($(event.target).attr('data-toggle') == 'do_not_collapse') {
                return false;
            }
        }).
        tooltip({
            'placement': 'right'
        });
    },

    // Execute before the ajax call to server
    onTagService: function(elID) {
        $('#form_' + elID + ' button')
            .attr('disabled', true)
            .addClass('disabled');
    },

    doneTagService: function(service) {
        $('#collapse_' + service.name_url).collapse('hide');
        $('#link_' + service.name_url + ' span').attr('class', 'status-tagged');

        $('#link_' + service.name_url).
            unbind().
            attr('data-toggle', 'do_not_collapse').
            on('click', function() {
                return false;
            });
    },

    failedTag: function() {
        $('form button')
            .attr('disabled', false)
            .removeClass('disabled');
    },

    getStatusClass: function(app) {
        return 'status-' + this.statusClassHash[app.status];
    },

    getStatClass: function(app) {
        // need to find app by name url
        return 'stat-' + this.statusClassHash[app.status];
    }

};
// This ends the UI object