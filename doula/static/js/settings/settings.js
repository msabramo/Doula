Settings = {
    init: function() {
        _mixin(this, AJAXUtil);

        // Class event handlers
        this.click = $.proxy(this, 'click');
        this.success = $.proxy(this, 'success');

        this.radios = $('input[name=\'notify_me\']');
        this.radios.on('click', this.click);

        this.bindToDataActions();
    },

    bindToDataActions: function() {
        $('.search-list li').on('click', _bind(this.subscribeToSiteOrService, this));
    },

    subscribeToSiteOrService: function(event) {
        $(event.target).toggleClass('active');
        // this.post('/active url');
    },

    click: function(e) {
        var url = '/settings';
        this.post(url, {'notify_me': $(e.target).val()}, this.success);
    },

    success: function() {

    }
};

$(document).ready(function() {
    Settings.init();
});