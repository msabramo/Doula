var ServiceLabel = {

  originalLabelWidths: {},
  DEFAULT_LABEL_LENGTH: 20,
  CHAR_MULTIPLIER: 6,

  init: function() {
    _mixin(this, AJAXUtil);

    $('a.edit-label')._on('click', this.handleLabelEdit, this);
    $('span.accord-title-label input')._on('blur', this.handleLabelLostFocus, this);
    $('span.accord-title-label input')._on('keydown', this.handleLabelKeydown, this, true);
  },

  handleLabelEdit: function(event, link) {
      var serviceName = link.data("service");
      var link = $("#label-for-" + serviceName);
      link.addClass('hidden');

      var input = $("#input-label-for-" + serviceName);
      this.resizeLabelInput(input);
      input.addClass('active').focus();
  },

  handleLabelLostFocus: function(event, input) {
      this.handleLabelSave(input);
  },

  handleLabelKeydown: function(event, input) {
      if (event.keyCode == 13) {
          this.handleLabelSave(input);
      }

      this.resizeLabelInput(input);
  },

  /**
  * Save the label to the backend. Update the UI.
  */
  handleLabelSave: function(input) {
      input.removeClass('active');

      var siteName = input.data("site");
      var serviceName = input.data("service");
      var label = $("#label-for-" + serviceName);
      var text = $.trim(input.val());
      label.html(text).removeClass('hidden');

      var url = '/sites/' + siteName + '/' + serviceName + '/label';
      var params = {'label': text};
      var msg = 'Saving label. Please be patient and stay awesome.';

      this.post(url, params, this.doneHandleLabelSave, null, msg);
  },

  doneHandleLabelSave: function(rslt) {
      // done
  },

  /**
  * Resize input as we type.
  */
  resizeLabelInput: function(input) {
      var text = input.val();

      if (!this.originalLabelWidths[input.attr('id')]) {
          this.originalLabelWidths[input.attr('id')] = input.width();
      }

      if (text.length > this.DEFAULT_LABEL_LENGTH) {
          var moreChars = text.length - this.DEFAULT_LABEL_LENGTH;
          input.css('width', this.originalLabelWidths[input.attr('id')] + (moreChars * this.CHAR_MULTIPLIER));
      }
  }

};

$(document).ready(function() {
  ServiceLabel.init();
});