var UI = (function() {
	// UI module handles the UI actions on the page
	
	var UI = {
	    toggleCheckboxes: function() {
	        var selectAllBox = this;
            
            $('#applications input[type="checkbox"]').each(function(index, checkbox) {
                checkbox.checked = $(selectAllBox).is(':checked');
            });
	    },
	    
	    hideTagForm: function(event) {
	        $(this).closest('form').addClass('hide');
	        
	        return false;
	    },
	    
	    showTagForms: function() {
	        var selectedCheckboxes = Array();
	        
	        $('.application input[type="checkbox"]').each(function(index, checkbox) {
                if(checkbox.checked) {
                    selectedCheckboxes.push(checkbox);
                }
            });
            
            for (var i=0; i < selectedCheckboxes.length; i++) {
                var id = selectedCheckboxes[i].id.replace('checkbox_select_', '');
                
                $('#tag_form_' + id).removeClass('hide');
            }
	    }
    };
    // This ends the UI module
    
    return UI;
})();

var Doula = (function() {
	// The main Doula Module
	var Doula = {
	    
	    init: function() {
	        this.bindEvents();
	    },
	    
	    bindEvents: function() {
	        // UI events
	        $('#selectAll').on('click', UI.toggleCheckboxes);
	        $('#tag_selected').on('click', UI.showTagForms);
	        $('button[value="cancel"]').on('click', UI.hideTagForm);
	        
	        // Business logic events
	        // alextodo figure out how to bind function to this context
	        $('button[value="revert"]').on('click', Doula.revertApp);
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
                }
            });
	    }
    };
    // This ends the main Doula module
    
    return Doula;
})();

$(document).ready(function() {
    Doula.init();
});