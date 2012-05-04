var AjaxUtil = {
    
    post: function(msg, url, params, onPass, onFail) {
        onPass = _bind(onPass, this);
        this._showProgressIndicator(msg);
        
        $.ajax({
              url: url,
              type: 'POST',
              data: this._getDataValues(params),
              success: function(rslt) {
                  AjaxUtil._hideProgressIndicator();
                  
                  var obj = $.parseJSON(rslt);

                  if(obj.success) {
                      onPass(obj);
                  }
                  else {
                      $.colorbox({
                          width: '650px',
                          height: '400px',
                          html: function() {
                              $('#dialog-error-msg').html(obj.msg);
                              return $('#dialog-html').html();
                          },
                          close: '<a id="error-dialog-close" style="color: black;" href="#" class="pow-btn btn error-dialog-close">Close</a>',
                          onOpen: function() {
                              $('#dialog-html').show();
                          },
                          onClosed: function() {
                              $('#dialog-html').hide();
                              return false;
                          }
                      });
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
    
    _showProgressIndicator: function(msg) {
        $('#progress-indicator-message').html(msg);
        
        var progressIndicator = $('#progress-indicator');
        // Center the element by setting the margin-left
        var marginLeft = ($(window).width() - progressIndicator.width()) / 2;

        
        progressIndicator.css('margin-left', marginLeft);
        progressIndicator.slideToggle(600).addClass('open');
    },
    
    _hideProgressIndicator: function() {
        $('#progress-indicator').slideToggle(300).removeClass('open');
    }
}