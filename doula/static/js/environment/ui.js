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
        // If a service should be tagged, return false
        $('a[data-toggle="do_not_collapse"]').click(
            function() { 
                return false; 
        });

        $('.collapse').collapse({
            parent: '#envs-accordion',
            toggle: false
        });
    },

    updateTooltips: function() {
        // Show a tooltip so that user understands that the
        // app cannot be tagged
        $('a[data-toggle="do_not_collapse"]').tooltip({
            'placement': 'right'
        });
    },
    
    // Execute before the ajax call to server
    onTagService: function(elID) {
        $('#form_' + elID + ' button')
            .attr('disabled', true)
            .addClass('disabled');
    },

    doneTagService: function(elID) {
        $('#collapse_' + elID).collapse('hide');
        $('#link_' + elID + ' span').attr('class', 'status-tagged');
        $('#link_' + elID).click(UI.rtf);
        $('#link_' + elID).attr('data-toggle', 'do_not_collapse');

        UI.updateTooltips();
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
    },

    rtf: function() {
        return false;
    }
    
};
// This ends the UI object