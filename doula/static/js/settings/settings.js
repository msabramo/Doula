Settings = {
    init: function() {
        _mixin(this, AJAXUtil);

        this.bindToDataActions();
    },

    bindToDataActions: function() {
        $('input[name=\'notify_me\']').on('click', $.proxy(this.saveSettings, this));
        $('.search-list li').on('click', $.proxy(this.subscribeToNotification, this));
    },

    subscribeToNotification: function(event) {
        if($(event.target).attr('id') != 'my_jobs') {
            $(event.target).toggleClass('active');
            this.saveSettings();
        }
    },

    saveSettings: function() {
        var notifyMe = $('input[name=notify_me]:checked').val();
        var subscribed_to = [];

        $('.search-list li.active').each(function(index, el) {
            var val = $(el).attr('data-value');
            if(val != 'my_jobs') subscribed_to.push(val);
        });

        var params = {'notify_me': notifyMe, subscribed_to: subscribed_to};
        var msg = 'Saving your settings. Please be patient and stay awesome.';
        this.post('/settings', params, this.doneSaveSettings, false, msg);
    },

    doneSaveSettings: function(rslt) {
        // Done
    }
};

$(document).ready(function() {
    Settings.init();
});