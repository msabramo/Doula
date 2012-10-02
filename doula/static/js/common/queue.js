QueuedItems = {

    // The maximum number of jobs shown for a service
    MAX_SERVICE_JOB_COUNT: 3,
    showInitialPollRequest: false,
    jobQueueCount: 0,
    jobsAndStatuses: {},
    queueFilters: {},

    init: function(kwargs) {
        _mixin(this, AJAXUtil);
        _mixin(this, DataEventManager);

        this.queueFilters = __queueFilters;

        // The queue shows the jobs by default. No need to ajax.
        // If a service name exist, then you'll need to show the first poll request
        if (this.queueFilters.service) this.showInitialPollRequest = true;

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
        var jobIDs = $.map(this.jobsAndStatuses, function(value, key) {
            return key;
        });

        $.each(data.queuedItems.reverse(), $.proxy(function(index, item) {
            if (jobIDs.length) {
                // We've already added the jobs to the web page. Only add new and updated jobs
                if (jobIDs.indexOf(item.id) > -1) {
                    // Job's been tracked. only add if the status has changed.
                    if (this.jobsAndStatuses[item.id] != item.status) {
                        $("#queue-jobs .queued_item[data-id='" + item.id + "']").replaceWith(item.html);
                        QueuedItems.publish('queue-item-changed', item);
                    }
                }
                else {
                    // Jobs never been tracked. Add it as a new job
                    $('#queue-jobs').prepend(item.html);
                }

                // Update jobs and statuses array
                this.jobsAndStatuses[item.id] = item.status;
            }
            else {
                // Adding jobs to the web page for the first time.
                // Only services show the initial poll request.
                if (this.showInitialPollRequest) {
                    if (this.jobQueueCount < this.MAX_SERVICE_JOB_COUNT) {
                        if (!this.jobsAndStatuses[item.id]) {
                            $('#queue-jobs').append(item.html);
                            this.jobQueueCount += 1;
                        }
                    }
                }

                // Update jobs and statuses array
                this.jobsAndStatuses[item.id] = item.status;
            }

            QueuedItems.publish('queue-item-changed', item);
        }, this));
    }
};

$(document).ready(function() {
    QueuedItems.init();
});