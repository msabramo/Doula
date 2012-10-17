QueueView = {

    // The maximum number of jobs shown for a service
    MAX_SERVICE_JOB_COUNT: 3,
    limitInitialQueueItems: false,
    firstRun: true,
    jobQueueCount: 0,
    jobsAndStatuses: {},
    queueFilters: {},
    bucket_id: 0,
    last_updated: 0,
    pollInterval: 2000,

    init: function(kwargs) {
        _mixin(this, AJAXUtil);
        _mixin(this, DataEventManager);

        this.queueFilters = __queueFilters;
        this.queueFilters.bucket_id = this.bucket_id;
        this.queueFilters.last_updated = this.last_updated;

        // If a service name exist, then you'll need to show all the jobs
        // from the first poll request
        if (this.queueFilters.service) {
            this.pollInterval = 1000;
            this.limitInitialQueueItems = true;
        }

        this.bindToUIActions();
    },

    bindToUIActions: function() {
        this.selectFilterByAndSortByLabels();

        // Poll now and poll every second from now on
        this.poll();
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
        this.post('/queue',
                  this.queueFilters,
                  $.proxy(this.updateJobStatuses, this),
                  $.proxy(this.failedJobUpdateStatus, this),
                  false);
    },

    /**
    *   Return the id's of all the jobs we're tracking in jobsAndStatuses
    */
    getJobIDs: function() {
        return $.map(this.jobsAndStatuses, function(value, key) {return key;} );
    },

    failedJobUpdateStatus: function() {
        this.pollAgain();
    },

    /**
    *   Add new queue jobs to the web page. Here is where we update the queue-jobs element.
    *   Any status changes to jobs will appear here.
    */
    updateJobStatuses: function(data) {
        if (data.has_changed) {
            this.queueFilters.bucket_id = data.query_bucket.id;
            this.queueFilters.last_updated = data.query_bucket.last_updated;

            var jobIDs = this.getJobIDs();
            if (data.query_bucket.jobs.length) $('#no-queue-items-warning').hide();

            $.each(data.query_bucket.jobs.reverse(), $.proxy(function(index, job) {
                if (jobIDs.length) {
                    // We've already added the jobs to the web page. Only add new and updated jobs
                    if (jobIDs.indexOf(job.id) > -1) {
                        // Job's been tracked. only add if the status has changed.
                        if (this.jobsAndStatuses[job.id] != job.status) {
                            $("#queue-jobs .queued_item[data-id='" + job.id + "']").replaceWith(job.html);
                            QueueView.publish('queue-item-changed', job);
                        }
                    }
                    else {
                        // Jobs never been tracked. Add it as a new job
                        $('#queue-jobs').prepend(job.html);
                    }

                    // Update jobs and statuses array
                    this.jobsAndStatuses[job.id] = job.status;
                }
                else {
                    // Adding jobs to the web page for the first time.
                    // Only services show the initial poll request.
                    if (this.jobQueueCount < this.MAX_SERVICE_JOB_COUNT || !this.limitInitialQueueItems) {
                        if (!this.jobsAndStatuses[job.id]) {
                            $('#queue-jobs').append(job.html);
                            this.jobQueueCount += 1;
                        }
                    }

                    // Update jobs and statuses array
                    this.jobsAndStatuses[job.id] = job.status;
                }
            }, this));
        }

        if (this.firstRun) {
            this.firstRun = false;
            this.showTheSelectedJobLog();
        }

        this.pollAgain();
    },

    pollAgain: function() {
        // Call poll again after the response
        setTimeout($.proxy(function() {
            this.poll();
        }, this), this.pollInterval);
    },

    showTheSelectedJobLog: function() {
        if ($(document.location.hash).length) {
            $(document.location.hash).click();
            $(document).scrollTop($(document.location.hash).offset().top);
        }
    }
};

$(document).ready(function() {
    QueueView.init();
});