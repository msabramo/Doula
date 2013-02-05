var Filter = {

    cookieName: '',
    filterableEls: $('.filterable'),

    init: function(cookieName) {
      this.cookieName = cookieName;

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
        $.cookie(this.cookieName, searchText, {expires: 180});
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
        var searchText = $.cookie(this.cookieName);

        $('#filter').val(searchText).keyup().focus();
    }
};