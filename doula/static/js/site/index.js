var SitesPage = {

    init: function() {
        this.showTooltips();
    },

    showTooltips: function() {
        $('a[rel="tooltip"]').on('click', function(event, a) {
            if ($(event.target).attr('data-toggle') == 'do_not_collapse') {
                return false;
            }
        }).
        tooltip({
            'placement': 'right'
        });
    }
};

SitesPage.init();