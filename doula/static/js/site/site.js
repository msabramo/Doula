// The main Site Module
var Site = {

    init: function() {
        _mixin(this, AJAXUtil);

        Data.init();

        this.bindToUIActions();
        this.bindToDataActions();
    },

    /*************
    UI Actions
    **************/

    bindToUIActions: function() {
        this.initFilter();
    },

    /*******************
    Filter Functionality
    ********************/

    filterableEls: $('.filterable'),

    initFilter: function() {
        $('#clear')._on('click', this.clearFilter, this);
        $('#filter')._on('keyup', this.filterServices, this, allowEventToBubble=true);
        this.initFilterBox();
    },

    clearFilter: function() {
        $('#filter').val('').keyup().focus();
    },

    filterServices: function(event, filter) {
        var searchText = $.trim(filter.val().toLowerCase());

        // Save to cookie for future searches
        $.cookie(this.getCookieName(), searchText);
        var searchArray = searchText.split(',');

        this.filterableEls.each($.proxy(function(i, el) {
            el = $(el);
            var filterData = el.data('filter-data').toLowerCase();

            if (searchText === '') {
                el.show();
            }
            else if (this.inSearchArray(searchArray, filterData)) {
                el.show();
            }
            else {
                el.hide();
            }
        }, this));
    },

    /**
    * Finds the text in the search array
    */
    inSearchArray: function(searchArray, text) {
        for(var i = 0; i < searchArray.length; i++) {
            var searchPart = $.trim(searchArray[i]);

            if (searchPart === '') continue;

            if (text.indexOf(searchPart) != -1) {
                return true;
            }
        }

        return false;
    },

    initFilterBox: function() {
        var searchText = $.cookie(this.getCookieName());

        $('#filter').val(searchText).keyup().focus();
    },

    getCookieName: function() {
        return 'serviceFilter.' + Data.name;
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

            var url = '/sites/' + Data.name_url + '/lock';
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