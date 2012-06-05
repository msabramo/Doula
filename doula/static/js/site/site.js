var Site = (function() {
  // The main Site Module
  var Site = {
      
    init: function() {
        SiteData.init();
        UI.init();
        
        this.bindEvents();
    },
    
    bindEvents: function() {
        $('form').on('submit', this.tag);
        $('input.tag').on('change', this.validateTag);
        $('textarea.commit').on('change', this.validateMsg);
        $('a.deploy').on('click', this.deployApplication);
    },

    deployApplication: function() {
        var app = SiteData.findAppByID($(this).attr('app-id'));
        SiteData.deployApplication(app);
        
        return false;
    },
    
    tag: function(event) {
        var appID = this.id.replace('form_', '');

        if(appID == 'site') Site.tagSite(appID);
        else Site.tagApplication(appID);
        
        return false;
    },

    tagSite: function() {
        var tag = $('#tag_site').val();
        var msg = $('#msg_site').val();
        
        UI.onTag();
        SiteData.tagSite(tag, msg);
    },

    tagApplication: function(appID) {
        var app = SiteData.findAppByID(appID);
        var tag = $('#tag_' + app.name_url).val();
        var msg = $('#msg_' + app.name_url).val();

        UI.onTagApp();
        SiteData.tagApp(app, tag, msg);
    },
    
    validateTag: function(event) {
        if(!this.value) {
            var app = SiteData.findAppByID(this.id.replace('tag_', ''));
            SiteData.revertAppTag(app, '', app.msg);
            UI.tagApp(app);
        }
    },
    
    validateMsg: function() {
        if(!this.value) {
            var app = SiteData.findAppByID(this.id.replace('msg_', ''));
            SiteData.revertAppTag(app, app.tag, '');
            UI.tagApp(app);
      }
    }
  };
  // This ends the main Site module
  
  return Site;
})();

$(document).ready(function() {
  Site.init();
});