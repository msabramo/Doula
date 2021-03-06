QueueView={MAX_SERVICE_JOB_COUNT:3,limitInitialQueueItems:false,firstRun:true,jobQueueCount:0,jobsAndStatuses:{},queueFilters:{},bucket_id:0,last_updated:0,pollInterval:2000,init:function(kwargs){_mixin(this,AJAXUtil);_mixin(this,DataEventManager);this.queueFilters=__queueFilters;this.queueFilters.bucket_id=this.bucket_id;this.queueFilters.last_updated=this.last_updated;this.limitInitialQueueItems=__limitInitialQueueItems;if(this.limitInitialQueueItems){this.pollInterval=1000;}
this.bindToUIActions();},bindToUIActions:function(){this.selectFilterByAndSortByLabels();this.poll();},selectFilterByAndSortByLabels:function(){var sortBy=this.queueFilters.sort_by;var filterBy=this.queueFilters.filter_by;$('ul.sort_by a').each(function(index,el){el=$(el);if(el.hasClass('sort_by')){if(el.attr('data-val')==sortBy){el.addClass('active');}
else{el.removeClass('active');}
el.attr('href','/queue?sort_by='+
el.attr('data-val')+'&filter_by='+filterBy);}
else{if(el.attr('data-val')==filterBy){el.addClass('active');}
else{el.removeClass('active');}
el.attr('href','/queue?sort_by='+
sortBy+'&filter_by='+el.attr('data-val'));}});},poll:function(){this.queueFilters.job_ids=JSON.stringify(this.getJobIDs());this.post('/queue',this.queueFilters,$.proxy(this.updateJobStatuses,this),$.proxy(this.failedJobUpdateStatus,this),false);},getJobIDs:function(){return $.map(this.jobsAndStatuses,function(value,key){return key;});},failedJobUpdateStatus:function(){this.pollAgain();},updateJobStatuses:function(data){if(data.has_changed){this.queueFilters.bucket_id=data.query_bucket.id;this.queueFilters.last_updated=data.query_bucket.last_updated;var jobIDs=this.getJobIDs();if(data.query_bucket.jobs.length)$('#no-queue-items-warning').hide();$.each(data.query_bucket.jobs.reverse(),$.proxy(function(index,job){if(jobIDs.length){if(jobIDs.indexOf(job.id)>-1){if(this.jobsAndStatuses[job.id]!=job.status){$("#queue-jobs .queued_item[data-id='"+job.id+"']").replaceWith(job.html);QueueView.publish('queue-item-changed',job);}}
else{$('#queue-jobs').prepend(job.html);}
this.jobsAndStatuses[job.id]=job.status;}
else{if(this.jobQueueCount<this.MAX_SERVICE_JOB_COUNT||!this.limitInitialQueueItems){if(!this.jobsAndStatuses[job.id]){$('#queue-jobs').append(job.html);this.jobQueueCount+=1;}}
this.jobsAndStatuses[job.id]=job.status;}},this));}
if(this.firstRun){this.firstRun=false;this.showTheSelectedJobLog();}
this.pollAgain();},pollAgain:function(){setTimeout($.proxy(function(){this.poll();},this),this.pollInterval);},showTheSelectedJobLog:function(){if($(document.location.hash).length){$(document.location.hash).click();$(document).scrollTop($(document.location.hash).offset().top);}}};$(document).ready(function(){QueueView.init();});