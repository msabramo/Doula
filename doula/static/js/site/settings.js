Settings = {
    init: function() {
        _mixin(this, AJAXUtil);

        // Class event handlers
        this.click = $.proxy(this, 'click');
        this.success = $.proxy(this, 'success');

        this.radios = $('input[name=\'notify_me\']');
        this.radios.on('click', this.click);
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