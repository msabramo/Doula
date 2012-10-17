$(document).ready(function() {
  // fix broken links to gravatar
  $.each($('img.gravatar'),function() {
    if (this.naturalWidth === 0 || this.naturalHeight === 0 || this.complete === false) {
        $(this).attr('src', '/images/anon-gravatar.png');
    }
  });
});