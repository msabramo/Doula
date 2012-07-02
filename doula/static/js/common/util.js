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
            func(event)
            return false;
        }, this));
    }
}

// Implements the publish subscribe model, using jquery
var DataEventManager = {
    subscribe: function(event, fn) {
        $(this).bind(event, fn);
    },
    
    publish: function(event, data) {
        $(this).trigger(event, data);
    }
}

// This class encapsulates all the common functionality of a standard
// get or post for this application
var AJAXUtil = {
    
    post: function(msg, url, params, onDone, onFail) {
        this._send(msg, 'POST', url, params, onDone, onFail);
    },
    
    get: function(msg, url, params, onDone, onFail) {
        this._send(msg, 'GET', url, params, onDone, onFail);
    },
    
    _send: function(msg, type, url, params, onDone, onFail) {
        $('#progress_bar').show();
        onDone = _bind(onDone, this);
        
        $.ajax({
              url: url,
              type: type,
              data: this._getDataValues(params),
              success: function(response) {
                $('#progress_bar').hide();
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
        });
    },
    
    _getDataValues: function(params) {
        var dataValues = '';
        var count = 0;
        
        for(var key in params) {
            if(dataValues != '') dataValues += '&';
            dataValues += key + '=' + encodeURIComponent(params[key]);
        }
        
        return dataValues;
    },
    
    _showStandardErrorMessage: function(rslt) {
        // alextodo, show standard error message too
        // no modals
        alert(rslt.msg);
    }
}