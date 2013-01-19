// Update the status of a job in the title
var UpdateJobStatus = {

  originalPageTitle: '',

  init: function() {
    QueueView.subscribe('queue-item-changed', $.proxy(this.updateJobStatus, this));
  },

  updateJobStatus: function(event, job) {
    if (!this.originalPageTitle) this.originalPageTitle = document.title;

    // Cycle button gets enabled once
    if (job.job_type == 'cycle_service') {
      if (job.status == 'failed') document.title = 'Cycle Job Failed';
      else if (job.status == 'complete') document.title = 'Cycle Job Succeeded';
    }
    else if (job.job_type == 'release_service') {
      if (job.status == 'failed') document.title = 'Release Job Failed';
      else if (job.status == 'complete') document.title = 'Release Job Succeeded';
    }

    setTimeout(this.resetTitle, 5000);
  },

  resetTitle: function() {
    document.title = UpdateJobStatus.originalPageTitle;
  }

};

$(document).ready(function() {
  UpdateJobStatus.init();
});