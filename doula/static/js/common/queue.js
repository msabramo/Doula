QueuedItems = {

    init: function(kwargs) {
        _mixin(this, AJAXUtil);
        _mixin(this, DataEventManager);

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
        this.selectActiveLabel();
    },

    selectActiveLabel: function() {
        var params = this.getQueryStringParams();
        var sortBy = params.sort_by ? params.sort_by : 'all';
        var filterBy =  params.filter_by ? params.filter_by : 'allusers';

        $('ul.sort_by a').each(function(index, el) {
            el = $(el);

            if (el.hasClass('sort_by')) {
                if (el.attr('data-val') == sortBy) {
                    el.addClass('active');
                }
                else {
                    el.removeClass('active');
                }

                el.attr('href', '/queue?sort_by='+
                    el.attr('data-val')+'&filter_by='+filterBy);
            }
            else {
                if (el.attr('data-val') == filterBy) {
                    el.addClass('active');
                }
                else {
                    el.removeClass('active');
                }

                el.attr('href', '/queue?sort_by='+
                    sortBy+'&filter_by='+el.attr('data-val'));
            }
        });
    },

    getQueryStringParams: function() {
        var params = {};
        var q = document.URL.split('?')[1];

        if (q !== undefined) {
            var vals = q.split('&');

            for(var i=0; i < vals.length; i++) {
                hash = vals[i].split('=');
                params[hash[0]] = hash[1];
            }
        }

        return params;
    },

    poll: function() {
        var url = '/queue';
        this.kwargs.last_updated = this.data.lastUpdated;
        this.get(url, this.kwargs, this.handle_updates, null, false);
    },

    handle_updates: function(data) {
        this.new_queued_items = data.new_queued_items;
        this.publishQueueItemChangeEvents(data);

        $.each(data.queued_items, function(index, queued_item) {
            var el = $(".queued_items > .queued_item[data-id='" + queued_item.id + "']");
            if(el.length > 0) {
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
                    el.replaceWith(queued_item.html);
                }
            }
        });

        if (data.new_queued_items.length > 0) {
            this.latest_notifications.show();
            // alextodo redo this.
            if(data.new_queued_items.length == 1) {
                this.latest_notifications.html('There is 1 new job to be displayed.');
            }
            else {
                this.latest_notifications.html('There are ' + data.new_queued_items.length + ' jobs to be displayed.');
            }
        }
    },

    allExistingItems: false,

    publishQueueItemChangeEvents: function(data) {
        var allItems = this.getAllItems(data);

        // on initial load, make the queued items existing items
        // because we don't want to report on those changes
        if(this.allExistingItems === false) {
            this.allExistingItems = data.queued_items;
        }

        for(var i = 0; i < allItems.length; i++) {
            var item = allItems[i];
            var foundExistingItem = this.findExistingItem(item.id);

            // New item
            if(!foundExistingItem) {
                QueuedItems.publish('queue-item-changed', item);
            }
            else if(foundExistingItem.status != item.status) {
                QueuedItems.publish('queue-item-changed', item);
            }
        }

        this.allExistingItems = allItems;
    },

    findExistingItem: function(itemID) {
        for(var i = 0; i < this.allExistingItems.length; i++) {
            if(this.allExistingItems[i].id == itemID) return this.allExistingItems[i];
        }

        return false;
    },

    getAllItems: function(data) {
        var ids = [];
        var uniqueItems = [];
        var allItems = data.new_queued_items.concat(data.queued_items);

        for(var i = 0; i < allItems.length; i++) {
            if(ids.indexOf(allItems[i].id) == -1) {
                ids.push(allItems[i].id);
                uniqueItems.push(allItems[i]);
            }
        }

        return uniqueItems;
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
    QueuedItems.init(__job_dict);
});