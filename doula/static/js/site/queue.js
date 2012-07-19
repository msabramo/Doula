QueuedItems = {
    init: function(kwargs) {
        _mixin(this, AJAXUtil);

        // Class event handlers
        this.poll = $.proxy(this, 'poll');
        this.handle_updates = $.proxy(this, 'handle_updates');
        this.show_latest_notifications = $.proxy(this, 'show_latest_notifications');

        // "Job Dict" arguments
        this.kwargs = {};
        if (kwargs !== undefined) {
            this.kwargs = kwargs;
        }

        // Elements
        this.latest_notifications = $('.latest_notifications');
        this.queued_items =  $('.queued_items');

        // Events
        this.latest_notifications.on('click', this.show_latest_notifications);

        this.data = $('.queued_items').data();
        window.setInterval(this.poll, 2000);
    },

    poll: function() {
        var url = '/queue';
        this.kwargs.last_updated = this.data.lastUpdated;
        this.get('poll', url, this.kwargs, this.handle_updates);
    },

    handle_updates: function(data) {
        this.new_queued_items = data.new_queued_items;

        $.each(data.queued_items, function(index, queued_item) {
            var el = $(".queued_items > .queued_item[data-id='" + queued_item.id + "']");

            if (queued_item.status == 'complete') {
                class_name = 'alert-success';
            }
            else if (queued_item.status == 'failed') {
                class_name = 'alert-danger';
            }
            else {
                class_name = 'alert-info';
            }

            if (!el.hasClass(class_name)) {
                el.removeClass('alert-info');
                el.addClass(class_name);
                el.children('.logs').html(queued_item.log);
            }
        });

        if (data.new_queued_items.length > 0) {
            this.latest_notifications.show();
            this.latest_notifications.html('There are ' + data.new_queued_items.length + ' jobs to be displayed.');
        }
    },

    show_latest_notifications: function() {
        var that = this;
        $.each(this.new_queued_items, function(index, new_queued_item) {
            that.latest_notifications.after(new_queued_item.html);
        });
        this.latest_notifications.hide();

        // Update last_updated timestamp
        timestamp = Math.round(new Date().getTime() / 1000);
        this.queued_items.data('lastUpdated', timestamp);
    }
};

$(document).ready(function() {
  QueuedItems.init();
});