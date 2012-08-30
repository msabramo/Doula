var Service = {

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
        $('#compare_dropdown1,#compare_dropdown2').
            bind('click change blur keydown', $.proxy(this.updateCompareURL, this));

        this.updateCompareURL();
    },

    updateCompareURL: function() {
        var tag1 = $('#compare_dropdown1').val();
        var tag2 = $('#compare_dropdown2').val();

        var urlArray = this.compareURL.split('/');
        var url = '';

        for(var i = 0; i < urlArray.length - 1; i++) {
            url += urlArray[i] + '/';
        }

        url += tag1 + '...' + tag2;

        if(this.compareURL) {
            $('#compare_url').attr('href', url);
            $('#compare_url').html('View differences between "' + tag1 + '" and "' + tag2 + '".');
        }
        else {
            $('#compare_url').attr('href', "http://code.corp.surveymonkey.com/");
            $('#compare_url').html('Comparison not available for this service.');
        }
    },

    /*
    * DATA ACTIONS
    */

    bindToDataActions: function() {

    }
};

$(document).ready(function() {
  Service.init();
});