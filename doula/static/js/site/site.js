var Site = (function() {
  // The main Site Module
  var Site = {

    init: function() {
        Data.init();
        UI.init();

        this.bindToDataActions();
    },

    bindToDataActions: function() {
        $('form').on('submit', this.tag);
        $('input.tag').on('change', this.validateTag);
        $('textarea.commit').on('change', this.validateMsg);
        $('a.deploy').on('click', this.deployService);
    },

    tag: function(event) {
        var serviceID = this.id.replace('form_', '');

        if(serviceID == 'site') Site.tagSite(serviceID);
        else Site.tagService(serviceID);

        return false;
    },

    tagSite: function() {
        var tag = $('#tag_site').val();
        var msg = $('#msg_site').val();

        UI.onTag();
        Data.tagSite(tag, msg);
    },

    tagService: function(serviceID) {
        var service = Data.findServiceByID(serviceID);
        var tag = $('#tag_' + service.name_url).val();
        var msg = $('#msg_' + service.name_url).val();

        UI.onTagService(service.name_url);
        Data.tagService(service, tag, msg);
    },

    validateTag: function(event) {
        if(!this.value) {
            var service = Data.findServiceByID(this.id.replace('tag_', ''));
            Data.revertServiceTag(service, '', service.msg);
            UI.tagService(service);
        }
    },

    validateMsg: function() {
        if(!this.value) {
            var service = Data.findServiceByID(this.id.replace('msg_', ''));
            Data.revertServiceTag(service, service.tag, '');
            UI.tagService(service);
      }
    }
  };
  // This ends the main Site module

  return Site;
})();

$(document).ready(function() {
  Site.init();
});