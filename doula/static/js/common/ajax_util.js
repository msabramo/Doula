var AjaxUtil = {
    
    post: function(msg, url, params, onPass, onFail) {
        onPass = _bind(onPass, this);
        this._showProgressIndicator(msg);
        
        // alextodo, see if we can bind to this _bind(onPass, this), then the previous call
        // doesn't have to bind to this!
        
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
                      // alextodo, need to make call to UI. failed whatever
                      // need a common way to show the error
                      alert(obj.msg);
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
        progressIndicator.slideToggle(700).addClass('open');
    },
    
    _hideProgressIndicator: function() {
        $('#progress-indicator').slideToggle(700).removeClass('open');
    }
}