QueuedItems = {

    // The maximum number of jobs shown for a service
    MAX_SERVICE_JOB_COUNT: 3,
    limitInitialQueueItems: false,
    firstRun: true,
    jobQueueCount: 0,
    jobsAndStatuses: {},
    queueFilters: {},

    init: function(kwargs) {
        _mixin(this, AJAXUtil);
        _mixin(this, DataEventManager);

        this.queueFilters = __queueFilters;

        // The queue shows the jobs by default. No need to ajax.
        // If a service name exist, then you'll need to show all the jobs
        // from the first poll request
        if (this.queueFilters.service) this.limitInitialQueueItems = true;

        this.bindToUIActions();
    },

    bindToUIActions: function() {
        this.selectFilterByAndSortByLabels();

        // Poll now and poll every second from now on
        this.poll();
        window.setInterval($.proxy(this.poll, this), 1000);
    },

    /***************
    SELECT LABELS ON QUERY PAGE
    ****************/

    selectFilterByAndSortByLabels: function() {
        var sortBy = this.queueFilters.sort_by;
        var filterBy = this.queueFilters.filter_by;

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
        this.queueFilters.job_ids = JSON.stringify(this.getJobIDs());
        this.post('/queue', this.queueFilters, $.proxy(this.updateJobStatuses, this), null, false);
    },

    /**
    *   Return the id's of all the jobs we're tracking in jobsAndStatuses
    */
    getJobIDs: function() {
        return $.map(this.jobsAndStatuses, function(value, key) {return key;} );
    },

    /**
    *   Add new queue items to the web page. Here is where we update the queue-jobs element.
    *   Any status changes to jobs will appear here.
    */
    updateJobStatuses: function(data) {
        var jobIDs = this.getJobIDs();

        if (data.queuedItems.length) $('#no-queue-items-warning').hide();

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
                if (this.jobQueueCount < this.MAX_SERVICE_JOB_COUNT || !this.limitInitialQueueItems) {
                    if (!this.jobsAndStatuses[item.id]) {
                        $('#queue-jobs').append(item.html);
                        this.jobQueueCount += 1;
                    }
                }

                // Update jobs and statuses array
                this.jobsAndStatuses[item.id] = item.status;
            }

            QueuedItems.publish('queue-item-changed', item);
        }, this));

        if (this.firstRun) {
            this.firstRun = false;
            this.showTheSelectedJobLog();
        }
    },

    showTheSelectedJobLog: function() {
        if ($(document.location.hash).length) {
            $(document.location.hash).click();

            // We have to wait till the log is open so that we get an accurate
            // reading on the height of the log element. Then we scroll to that element
            setTimeout(function() {
                var id = document.location.hash.replace('#', '').trim();
                var logHeight = $('#item_' + id).height();
                var destination = $(document.location.hash).offset().top + logHeight;
                $(document).scrollTop(destination);
            }, 400);
        }
    }
};

$(document).ready(function() {
    QueuedItems.init();
});