$(document).ready(function() {
  // fix broken links to gravatar
  $.each($('img.gravatar'),function() {
    if (this.naturalWidth === 0 || this.naturalHeight === 0 || this.complete === false) {
        $(this).attr('src', '/images/anon-gravatar.png');
    }
  });

  // Initialize the popovers for bootstrap
  setTimeout(function() {
    $('[rel="popover"]').popover();
    $('[rel="tooltip"]').tooltip();
  }, 500);

  // Set the horizontal position of the feedback tab
  setSideTab = function() {
    var st = $('.side_tab');
    var cnt = $('.content');

    st.css({'left': cnt.position().left + cnt.width() + st.width()});
  };

  setTimeout(setSideTab, 500);

  $(window).on('resize', function() {
    setSideTab();
  });

  // Scroll for docs
  if (document.location.href.match(/docs/)) {
    var sideBarEl = $('#docs-sidebar');
    var ogTop = sideBarEl.offset().top;

    scrollSideTab = function() {
      var scrollTop = window.pageYOffset || document.documentElement.scrollTop  || document.body.scrollTop;

      if(scrollTop >= ogTop) {
        var scrollTop = scrollTop - ogTop + 7 + 'px';
        sideBarEl.css('marginTop', scrollTop);
      }
      else{
        scrollTop - 7 + 'px';
        sideBarEl.css('marginTop', scrollTop);
      }
    }

    $(window).on('scroll', scrollSideTab);
  }

  /* Click away for help docs */

  /**
  *   When the user clicks away from an element we hide the element. For example a settings
  *   pane should be hidden when the user clicks away.
  */
  _hideElementWhenUserClicksAway = function(selector, onClickAway) {
    $('body').bind('click', function(e) {
      // If the user clicks outside of the form, hide it.
      closestElements = $(e.target).closest(selector);
      elementsOfInterest = $(selector);

      // If the element clicked isn't part of what was clicked, hide the element
      if (closestElements.length === 0) {
        if (elementsOfInterest.is(':visible')) {
          if (typeof(onClickAway) == 'function') onClickAway(e);
          else elementsOfInterest.hide();
        }
      }
    });
  };

  _hideElementWhenUserClicksAway('[rel="popover"]', function() {
    // Hide all the elements
    $('[rel="popover"]').popover('hide');
  });

});