_mixin=function(target,source){for(var x in source){target[x]=source[x];}};var DataEventManager={subscribe:function(event,fn){$(this).bind(event,fn);},publish:function(event,data){$(this).trigger(event,data);}};_inArray=function(key,array,attribute){for(var i=0;i<array.length;i++){var item=array[i];if(typeof(item)=='object'){if(key==item[attribute])return item;}
else{if(key==item)return item;}}
return false;};_withoutArray=function(array,key,attribute){var arrayWithout=[];for(var i=0;i<array.length;i++){var item=array[i];if(typeof(item)=='object'){if(array!=item[attribute])arrayWithout.push(item);}
else{if(array!=item)arrayWithout.push(item);}}
return arrayWithout;};var AJAXUtil={post:function(url,params,onDone,onFail,msg){this._send('POST',url,params,onDone,onFail,msg);},get:function(url,params,onDone,onFail,msg){this._send('GET',url,params,onDone,onFail,msg);},_send:function(type,url,params,onDone,onFail,msg){onDone=$.proxy(onDone,this);if(typeof(onFail)=='function')onFail=$.proxy(onFail,this);if(msg)Notifier.info(msg,false);$.ajax({url:url,type:type,data:this._getDataValues(params),error:function(){if(typeof(onFail)=='function'){onFail(rslt);}
else{AJAXUtil._showStandardErrorMessage(rslt);}},success:function(response){try{if(msg){setTimeout(function(){Notifier.hide();},1500);}
rslt=(typeof(response)=='string')?$.parseJSON(response):response;if(rslt.success){onDone(rslt);}
else{if(typeof(onFail)=='function'){onFail(rslt);}
else{Notifier.hide();AJAXUtil._showStandardErrorMessage(rslt);}}}
catch(err){onDone(response);}}});},_getDataValues:function(params){var dataValues='';var count=0;for(var key in params){if(dataValues!=='')dataValues+='&';dataValues+=key+'='+encodeURIComponent(params[key]);}
return dataValues;},_showStandardErrorMessage:function(rslt){$('#modal-error').on('show',function(){$('#modal-error-msg').html(rslt.msg);$('#modal-error-close').on('click',function(){$('#modal-error').modal('hide');return false;});});$('#modal-error').modal();}};;QueueView={MAX_SERVICE_JOB_COUNT:3,limitInitialQueueItems:false,firstRun:true,jobQueueCount:0,jobsAndStatuses:{},queueFilters:{},bucket_id:0,last_updated:0,pollInterval:2000,init:function(kwargs){_mixin(this,AJAXUtil);_mixin(this,DataEventManager);this.queueFilters=__queueFilters;this.queueFilters.bucket_id=this.bucket_id;this.queueFilters.last_updated=this.last_updated;this.limitInitialQueueItems=__limitInitialQueueItems;if(this.limitInitialQueueItems){this.pollInterval=1000;}
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
this.pollAgain();},pollAgain:function(){setTimeout($.proxy(function(){this.poll();},this),this.pollInterval);},showTheSelectedJobLog:function(){if($(document.location.hash).length){$(document.location.hash).click();$(document).scrollTop($(document.location.hash).offset().top);}}};$(document).ready(function(){QueueView.init();});;