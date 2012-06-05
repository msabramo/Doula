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
                          height: '300px',
                          html: function() {
                              $('.error-dialog div').html(obj.msg);
                              return $('#dialog-html').html();
                          },
                          close: '<a href="#" class="pow-btn btn error-dialog-close">Close</a>',
                          onOpen: function() {
                              $('#dialog-html').show();
                          },
                          onComplete: function() {
                              $('#cboxClose a').on('click', function() {
                                $.colorbox.close();
                                return false;
                              });
                          },
                          onClosed: function() {
                              $('#dialog-html').hide();
                              return false;
                          }
                      });

                      if(onFail) onFail(rslt);
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
        
        AjaxUtil._positionProgressIndicator();
        $(window).resize(AjaxUtil._positionProgressIndicator);

        $('#progress-indicator').slideToggle(600).addClass('open');
    },

    _positionProgressIndicator: function() {
        var pi = $('#progress-indicator');
        pi.css('width', $('#content').width());

        // Center the element by setting the margin-left
        var marginLeft = ($(window).outerWidth(true) - pi.outerWidth(true)) / 2;

        pi.css('right', marginLeft + 'px');
    },
    
    _hideProgressIndicator: function() {
        $(window).unbind('resize');
        $('#progress-indicator').slideToggle(300).removeClass('open');
    }
}