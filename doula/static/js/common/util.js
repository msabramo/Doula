// Stolen from underscore, because this is all I needed

// Reusable constructor function for prototype setting.
var ctor = function() { };
var nativeBind = Function.prototype.bind;
var toString = Object.prototype.toString;
var slice = Array.prototype.slice;

// Is a given value a function?
_isFunction = function(obj) {
  return toString.call(obj) == '[object Function]';
};

// Create a function bound to a given object (assigning `this`, and arguments,
// optionally). Binding with arguments is also known as `curry`.
// Delegates to **ECMAScript 5**'s native `Function.bind` if available.
// We check for `func.bind` first, to fail fast when `func` is undefined.
_bind = function bind(func, context) {
  var bound, args;
  if (func.bind === nativeBind && nativeBind) return nativeBind.apply(func, slice.call(arguments, 1));
  if (!_isFunction(func)) throw new TypeError;
  args = slice.call(arguments, 2);

  return bound = function() {
    if (!(this instanceof bound)) return func.apply(context, args.concat(slice.call(arguments)));
    ctor.prototype = func.prototype;
    var self = new ctor;
    var result = func.apply(self, args.concat(slice.call(arguments)));
    if (Object(result) === result) return result;
    return self;
  };
};

// Mixin the attributes and functions from the source object
// to the target object
_mixin = function(target, source) {
    for(var x in source) {
        target[x] = source[x];
    }
};

var EventUtil = {

    onclick: function(selector, func) {
        $(selector).on('click', _bind(function(event) {
            func = _bind(func, this);
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
        onDone = _bind(onDone, this);
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
        // alextodo, show standard error message too
        // no modals
        alert(rslt.msg);
    }
};