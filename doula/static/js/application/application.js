var Application = {
    
    compareURL: '',

    init: function() {
        this.compareURL = __compare_url;
        this.bindToUIActions();
        this.bindToDataActions();
    },
    
    /*
    * UI ACTIONS
    */
    
    bindToUIActions: function() {
    	$('.sm-side-tab').sideTab();
    	
    	$('#compare_dropdown1,#compare_dropdown2').
    	    bind('click change blur keydown', _bind(this.updateCompareURL, this));
    	
    	this.updateCompareURL();
    },
    
    updateCompareURL: function() {
        var tag1 = $('#compare_dropdown1').val();
        var tag2 = $('#compare_dropdown2').val()
        
        var urlArray = this.compareURL.split('/');
        var url = '';

        for(var i = 0; i < urlArray.length - 1; i++) {
            url += urlArray[i] + '/';
        }
        
        $('#compare_url').attr('href', url + tag1 + '...' + tag2);
        $('#compare_url').html('View differences between "' + tag1 + '" and "' + tag2 + '".');
    },
    
    /*
    * DATA ACTIONS
    */
    
    bindToDataActions: function() {

    }
};

$(document).ready(function() {
  Application.init();
});