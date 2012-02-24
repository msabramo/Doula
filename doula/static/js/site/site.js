var Site = (function() {
    
	// The main Site Module
	var Site = {
	    
	    init: function() {
	        this.bindEvents();
	        SiteData.init();
	    },
	    
	    bindEvents: function() {
	        // UI events
	        $('#selectAll').on('click', UI.toggleCheckboxes);
	        $('#tag_selected').on('click', this.tagSelected);
	        $('button[value="cancel"]').on('click', UI.hideTagForm);
	        
	        // Business logic events
	        // alextodo figure out how to bind function to this context
	        $('button[value="revert"]').on('click', Site.revertApp);
	        
	        // alextodo, handle the actual submission code
	        // after submission, the app turns to grey cause it's committable
	    },
	    
	    tagSelected: function() {
	        // alextodo show errro message for bad status forms
	        UI.showTagForms();
	    },
	    
	    revertApp: function() {
	        var appID = this.id.replace('revert_', '')
	        
	        $.ajax({
                url: "/sites/app/revert/",
                type: 'POST',
                data : { 
                    'id': appID,
                },
                
                success: function(result) {
                    app = jQuery.parseJSON(result.app);
                    
                    $('#revert_' + app.id).addClass('hide');
                    $('#application_' + app.id).replaceWith(result.html);
                    // alextodo need to make only remove if no other uncommitted changes
                    $('#tag_deployment').removeClass('disabled');
                    $('#errors_' + app.id).addClass('hide');
                    
                    // Rebind events
                    Site.bindEvents();
                }
            });
	    }
    };
    // This ends the main Site module
    
    return Site;
})();

$(document).ready(function() {
    Site.init();
});