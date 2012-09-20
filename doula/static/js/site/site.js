// The main Site Module
var Site = {

    init: function() {
        _mixin(this, AJAXUtil);

        Data.init();
        UI.init();

        this.bindToDataActions();
    },

    bindToDataActions: function() {
        $('form').on('submit', this.tag);
        $('input.tag').on('change', this.validateTag);
        $('textarea.commit').on('change', this.validateMsg);
        $('a.deploy').on('click', this.deployService);
        $('#lock-site').on('click', $.proxy(this.toggleSiteLock, this));
    },

    tag: function(event) {
        var serviceID = this.id.replace('form_', '');

        if(serviceID == 'site') Site.tagSite(serviceID);
        else Site.tagService(serviceID);

        return false;
    },

    tagSite: function() {
        var tag = $('#tag_site').val();
        var msg = $('#msg_site').val();

        UI.onTag();
        Data.tagSite(tag, msg);
    },

    tagService: function(serviceID) {
        var service = Data.findServiceByID(serviceID);
        var tag = $('#tag_' + service.name_url).val();
        var msg = $('#msg_' + service.name_url).val();

        UI.onTagService(service.name_url);
        Data.tagService(service, tag, msg);
    },

    validateTag: function(event) {
        if(!this.value) {
            var service = Data.findServiceByID(this.id.replace('tag_', ''));
            Data.revertServiceTag(service, '', service.msg);
            UI.tagService(service);
        }
    },

    validateMsg: function() {
        if(!this.value) {
            var service = Data.findServiceByID(this.id.replace('msg_', ''));
            Data.revertServiceTag(service, service.tag, '');
            UI.tagService(service);
      }
    },

    /****************
    SITE LOCK/UNLOCK
    *****************/

    toggleSiteLock: function(event) {
        var lockButton = $(event.target);

        if (!lockButton.hasClass('disabled')) {
            // Default to lock the site since it's unlocked
            var params = {'lock': 'true'};
            var msg = 'Locking site. Please be patient and stay awesome.';

            if (lockButton.hasClass('locked')) {
                // unlock the site since it's locked
                params = {'lock': 'false'};
                msg = 'Unlocking site. Please be patient and stay awesome.';
            }

            var url = '/sites/' + Data.name_url + '/lock';
            this.post(url, params, this.doneToggleSiteLock, false, msg);
        }

        return false;
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