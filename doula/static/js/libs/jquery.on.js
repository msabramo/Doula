(function( $ ) {
  // A custom 'on' function that always returns false
  // and prevents the default event bubbling

  // It makes for simpler cleaner function bindings. Leaving the
  // resulting function 1000% more testable.

  $.fn._on = function(eventType, func, context, allowEventToBubble) {
    // If the context isn't passed in set it to false. never proxy the function.
    context = context || false;
    allowEventToBubble = allowEventToBubble || false;

    this.on(eventType, $.proxy(function(event) {
        var target = (event.target) ? $(event.target) : [];
        if (context) func = $.proxy(func, context);
        func(event, target);

        if (!allowEventToBubble) {
          event.preventDefault();
          return false;
        }
      }, context));
    };

    return this;
})( jQuery );