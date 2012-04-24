var Application = {

    init: function() {
    	this.bindDataActions();
    	this.bindUIActions();
    },

    bindUIActions: function() {
    	$('.sm-side-tab').sideTab();
    },

    bindDataActions: function() {

    }
};

$(document).ready(function() {
  Application.init();
});