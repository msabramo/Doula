var Doula = (function() {
	// The main Doula Module
	var Doula = {
	    
	    init: function() {
	        this.bindEvents();
	    },
	    
	    bindEvents: function() {
	        $('#selectAll').on('click', this.toggleCheckboxes);
	        $('#cancel_comment').on('click', this.cancelComment);
	        $('#tag_selected').on('click', this.tagSelected);
	    },
	    
	    toggleCheckboxes: function() {
	        var selectAllBox = this;
            
            $('#applications input[type="checkbox"]').each(function(index, checkbox) {
                checkbox.checked = $(selectAllBox).is(':checked');
            });
	    },
	    
	    cancelComment: function() {
	        console.log(this);
	        $(this).closest('form').addClass('hide');
	        return false;
	    },
	    
	    tagSelected: function() {
	        var selectedCheckboxes = Array();
	        
	        $('#applications input[type="checkbox"]').each(function(index, checkbox) {
                if(checkbox.checked) {
                    selectedCheckboxes.push(checkbox);
                }
            });
            
            for (var i=0; i < selectedCheckboxes.length; i++) {
                var id = selectedCheckboxes[i].id.replace('checkbox_select_', '');
                
                $('#tag_form_' + id).removeClass('hide');
            }
            
            console.log(selectedCheckboxes);
	    }
    };
    // This ends the main Doula module
    
    return Doula;
})();

$(document).ready(function() {
    Doula.init();
});