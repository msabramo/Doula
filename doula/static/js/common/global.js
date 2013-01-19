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

});