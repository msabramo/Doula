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
        $("#accordion").accordion();
        // If you cannot tag because of uncommitted changes
        // bind a function that will nullify the link click
        $('a.keyCloser').on('click', function() { return false; });
        $('.sm-side-tab').sideTab();
    },
    
    // Execute before the ajax call to server
    onTag: function() {
        $('form input.btn')
            .attr('disabled', true)
            .addClass('disabled');
    },
    
    deployApp: function(app) {
        $('#deploy_' + app.name_url).hide();
        $('#panel_' + app.name_url + ' strong').html('Deployed');
        this.updateStatus(app.name_url);
    },

    doneTagApp: function(elID) {
        $('#panel_' + elID).click();
        // You can no longer tag an app after it's been tagged
        $('#panel_' + elID).on('click', function() { return false; });
        $('#panel_' + elID + ' strong').html('Tagged');
        $('#panel_' + elID + ' em').hide();
        $('#deploy_' + elID).removeClass('hide');

        this.updateStatus(elID);
    },

    failedTag: function() {
        $('form input.btn')
            .attr('disabled', false)
            .removeClass('disabled');
    },
    
    updateStatus: function(elID) {
        $('#stat_' + elID)
            .removeClass('stat-changed stat-error stat-tagged')
            .addClass(this.getStatClass(app));
        
        $('#status_' + elID)
            .removeClass('status-changed status-error status-tagged')
            .addClass(this.getStatusClass(app));
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