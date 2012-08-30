// Mixin the attributes and functions from the source object
// to the target object
_mixin = function(target, source) {
    for(var x in source) {
        target[x] = source[x];
    }
};

var EventUtil = {

    onclick: function(selector, func) {
        $(selector).on('click', $.proxy(function(event) {
            func = $.proxy(func, this);
            func(event);
            return false;
        }, this));
    }
};

// Implements the publish subscribe model, using jquery
var DataEventManager = {
    subscribe: function(event, fn) {
        $(this).bind(event, fn);
    },

    publish: function(event, data) {
        $(this).trigger(event, data);
    }
};

// Extends the string object with function in to check
// if the string exist in the array, or as an attribute of the array
_inArray = function(key, array, attribute) {
  for(var i = 0; i < array.length; i++) {
    var item = array[i];

    if(typeof(item) == 'object') {
      if(key == item[attribute]) return item;
    }
    else {
      if(key == item) return item;
    }
  }

  return false;
};

_withoutArray = function(array, key, attribute) {
  var arrayWithout = [];

  for(var i = 0; i < array.length; i++) {
    var item = array[i];

    if(typeof(item) == 'object') {
      if(array != item[attribute]) arrayWithout.push(item);
    }
    else {
      if(array != item) arrayWithout.push(item);
    }
  }

  return arrayWithout;
};

// This class encapsulates all the common functionality of a standard
// get or post for this application
var AJAXUtil = {

    post: function(url, params, onDone, onFail, showProgressBar) {
        this._send('POST', url, params, onDone, onFail, showProgressBar);
    },

    get: function(url, params, onDone, onFail, showProgressBar) {
        this._send('GET', url, params, onDone, onFail, showProgressBar);
    },

    _send: function(type, url, params, onDone, onFail, showProgressBar) {
        onDone = $.proxy(onDone, this);
        if(typeof(onFail) == 'function') onFail = $.proxy(onFail, this);
        if(showProgressBar !== false) $('#progress-section').show();

        $.ajax({
              url: url,
              type: type,
              data: this._getDataValues(params),
              success: function(response) {
                  try {
                    // Progress the progress bar to the end
                    setTimeout(function() {
                      $('.polyfill')[0].style.animationDuration = '1300ms';
                      $('.polyfill')[0].style.mozAnimationDuration = '1300ms';
                      $('.polyfill')[0].style.webkitAnimationDuration = '1300ms';
                    }, 200);

                    setTimeout(function() {
                      if(showProgressBar !== false) $('#progress-section').fadeOut('slow');
                    }, 400);

                    rslt = (typeof(response) == 'string') ?
                    $.parseJSON(response) : response;

                    if(rslt.success) {
                        onDone(rslt);
                    }
                    else {
                        if(typeof(onFail) == 'function') {
                            onFail(rslt);
                        }
                        else {
                            AJAXUtil._showStandardErrorMessage(rslt);
                        }
                    }
                  }
                  catch(err) {
                    // response isn't JSON, simple HTML
                    onDone(response);
                  }
              }
        });
    },

    _getDataValues: function(params) {
        var dataValues = '';
        var count = 0;

        for(var key in params) {
            if(dataValues !== '') dataValues += '&';
            dataValues += key + '=' + encodeURIComponent(params[key]);
        }

        return dataValues;
    },

    _showStandardErrorMessage: function(rslt) {
        $('#modal-error').on('show', function () {
          $('#modal-error-msg').html(rslt.msg);
          $('#modal-error-close').on('click', function() {
            $('#modal-error').modal('hide');
            return false;
          });
        });

        $('#modal-error').modal();
    }
};