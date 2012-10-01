QueuedItems = {

    // The maximum number of jobs shown for a service
    MAX_SERVICE_JOB_COUNT: 3,
    jobQueueCount: 0,
    jobsAndStatuses: {},
    queueFilters: {},

    init: function(kwargs) {
        _mixin(this, AJAXUtil);
        _mixin(this, DataEventManager);

        this.queueFilters = __queueFilters;
        this.bindToUIActions();
    },

    bindToUIActions: function() {
        this.selectFilterByAndSortByLabels();
        // Poll every second for updates
        window.setInterval($.proxy(this.poll, this), 1000);
    },

    /***************
    SELECT LABELS ON QUERY PAGE
    ****************/

    selectFilterByAndSortByLabels: function() {
        var sortBy = this.queueFilters.sortBy;
        var filterBy = this.queueFilters.filterBy;

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

    /***********************
    POLL BACKEND FOR UPDATES
    ************************/

    poll: function() {
        var params = {
            "service": this.queueFilters.service,
            "sort_by": this.queueFilters.sort_by,
            "filter_by": this.queueFilters.filterBy,
            "jobs_started_after": this.queueFilters.jobsStartedAfter,
            "jobs_and_statuses": JSON.stringify(this.jobsAndStatuses)
        };

        this.post('/queue', params, $.proxy(this.updateJobStatuses, this), null, false);
    },

    updateJobStatuses: function(data) {
        var currentNumberOfJobs = $('#queue-jobs .queued_item').length;

        $.each(data.queuedItems.reverse(), $.proxy(function(index, item) {
            var el = $("#queue-jobs .queued_item[data-id='" + item.id + "']");

            if(el.length > 0) {
                // queue item already exist. just update the existing HTML
                if(el.attr('data-status') != item.status) {
                    el.replaceWith(item.html);
                    QueuedItems.publish('queue-item-changed', item);
                }
            }
            else {
                // Adding the HTML for the first time
                if (currentNumberOfJobs) {
                    // Jobs already existed on the page. not the first job visually
                    $('#queue-jobs').prepend(item.html);
                    // Update jobs and statuses array
                    this.jobsAndStatuses[item.id] = item.status;
                }
                else {
                    // Adding jobs to web page for the first time.
                    if (this.jobQueueCount < this.MAX_SERVICE_JOB_COUNT) {
                        $('#queue-jobs').append(item.html);
                        this.jobQueueCount += 1;

                        // Update jobs and statuses array
                        this.jobsAndStatuses[item.id] = item.status;
                    }
                }

                QueuedItems.publish('queue-item-changed', item);
            }
        }, this));
    }
};

$(document).ready(function() {
    QueuedItems.init();
});