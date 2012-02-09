var Doula = (function() {
	// The main Doula Module
	var Doula = {
	    
	    init: function() {
	        this.bindEvents();
	    },
	    
	    bindEvents: function() {
	        $('#selectAll').on('click', function() {
	            var selectAllBox = this;
	            
	            $('#applications input[type="checkbox"]').each(function(index, checkbox) {
	                checkbox.checked = $(selectAllBox).is(':checked');
	            });
	        });
	    }
    };
    // This ends the main Doula module
    
    return Doula;
})();

$(document).ready(function() {
    Doula.init();
});