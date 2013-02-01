// The main Site Module
var Site = {

    init: function() {
        this.site = __site;

        _mixin(this, AJAXUtil);

        this.bindToUIActions();
        this.bindToDataActions();
    },

    /*************
    UI Actions
    **************/

    bindToUIActions: function() {
        Filter.init('serviceFilter.' + this.site.name);
    },

    /*************
    Data Actions
    **************/

    bindToDataActions: function() {
        $('#lock-site')._on('click', this.toggleSiteLock, this);
    },

    /****************
    SITE LOCK/UNLOCK
    *****************/

    toggleSiteLock: function(event, lockButton) {
        if (!lockButton.hasClass('disabled')) {
            // Default to lock the site since it's unlocked
            var params = {'lock': 'true'};
            var msg = 'Locking site. Please be patient and stay awesome.';

            if (lockButton.hasClass('locked')) {
                // unlock the site since it's locked
                params = {'lock': 'false'};
                msg = 'Unlocking site. Please be patient and stay awesome.';
            }

            var url = '/sites/' + this.site.name_url + '/lock';
            this.post(url, params, this.doneToggleSiteLock, false, msg);
        }
    },

    doneToggleSiteLock: function(rslt) {
        // toggle the current state of the button on round trip
        var lockButton = $('#lock-site');

        if (lockButton.hasClass('locked')) {
            lockButton.
                removeClass('locked').
                addClass('unlocked').
                html('<i class="icon-lock icon-black"></i> Lock Site');
        }
        else {
            lockButton.
                removeClass('unlocked').
                addClass('locked').
                html('<i class="icon-lock icon-black"></i> Unlock Site');
        }
    }
};

$(document).ready(function() {
  Site.init();
});