var Site = (function() {
    
	// The main Site Module
	var Site = {
	    
	    init: function() {
	        this.bindEvents();
	        SiteData.init();
	    },
	    
	    bindEvents: function() {
	        // UI only events events
	        $('#selectAll').on('click', UI.toggleCheckboxes);
	        $('#tag_selected').on('click', this.tagApplication);
	        $('button[value="cancel"]').on('click', UI.hideTagApplicationForm);
	        
	        // Data events
	        $('button[value="revert"]').on('click', Site.revertApplication);
	    },
	    
	    tagApplication: function() {
	        UI.showTagApplicationForm();
	    },
	    
	    revertApplication: function() {
	        var appID = this.id.replace('revert_', '')
	        // alextodo make this url available on backend
	        // alextodo, continue with this shinigan
	        
	        $.post({
                url: "/sites/app/revert/",
                data : { 'id': appID },
                success: function(data) {
                    app = jQuery.parseJSON(data.app);
                    Site.passRevertApplication(app);
                }
            });
	    },
	    
	    passRevertApplication: function(app) {
	        $('#revert_' + app.id).addClass('hide');
            $('#application_' + app.id).replaceWith(result.html);
            // alextodo need to make only remove if no other uncommitted changes
            $('#tag_deployment').removeClass('disabled');
            $('#errors_' + app.id).addClass('hide');
            
            // Rebind events
            Site.bindEvents();
	    }
    };
    // This ends the main Site module
    
    return Site;
})();

$(document).ready(function() {
    Site.init();
});