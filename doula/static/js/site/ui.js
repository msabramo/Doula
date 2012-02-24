var UI = {
    toggleCheckboxes: function() {
        var selectAllBox = this;
        
        $('.application input[type="checkbox"]').each(function(index, checkbox) {
            if(!checkbox.disabled) checkbox.checked = $(selectAllBox).is(':checked');
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
                if(checkbox.value == 'uncommitted_changes') {
                    // alextodo, how do we handle errors on page?
                    var id = checkbox.id.replace('checkbox_select_', '');
                    $('#errors_' + id).removeClass('hide');
                }
                else {
                    selectedCheckboxes.push(checkbox);
                }
            }
        });
        
        for (var i=0; i < selectedCheckboxes.length; i++) {
            var id = selectedCheckboxes[i].id.replace('checkbox_select_', '');
            
            $('#tag_form_' + id).removeClass('hide');
        }
    }
};
// This ends the UI object