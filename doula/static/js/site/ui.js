var UI = {
    
    toggleCheckboxes: function() {
        var selectAllBox = this;
        
        $('.application :checkbox').each(function(index, checkbox) {
            if(!checkbox.disabled) checkbox.checked = $(selectAllBox).is(':checked');
        });
    },
    
    hideTagApplicationForm: function(event) {
        $(this).closest('form').addClass('hide');
        
        return false;
    },
    
    showTagApplicationForm: function() {
        $('.application :checked').each(function(index, checkbox) {
            if(checkbox.value == 'uncommitted_changes') {
                var id = checkbox.id.replace('checkbox_select_', '');
                $('#errors_' + id).removeClass('hide');
            }
            else {
                var id = checkbox.id.replace('checkbox_select_', '');
                $('#tag_form_' + id).removeClass('hide');
            }
        });
    }
};
// This ends the UI object