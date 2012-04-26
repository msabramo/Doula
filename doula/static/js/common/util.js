// Stolen from underscore, because this is all I needed

// Reusable constructor function for prototype setting.
var _ctor = function() { };
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
    _ctor.prototype = func.prototype;
    var self = new _ctor;
    var result = func.apply(self, args.concat(slice.call(arguments)));
    if (Object(result) === result) return result;
    return self;
  };
};

_mixin = function(target, source) {
    for(var x in source) {
        target[x] = source[x];
    }
}