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
return dataValues;},_showStandardErrorMessage:function(rslt){$('#modal-error').on('show',function(){$('#modal-error-msg').html(rslt.msg);$('#modal-error-close').on('click',function(){$('#modal-error').modal('hide');return false;});});$('#modal-error').modal();}};