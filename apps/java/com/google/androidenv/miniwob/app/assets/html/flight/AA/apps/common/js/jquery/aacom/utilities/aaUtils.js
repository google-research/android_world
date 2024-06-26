jQuery.aaFormFieldEffects = function() {
  var self = this;
  self.forms = jQuery('form');
  self.fieldsets = jQuery(self.forms).find('fieldset');
  self.inputs = jQuery(self.forms).find('input');
  self.fieldsets.click(function(e) {
    self.resetFocus();
    self.focusFieldset(jQuery(this));
  });
  self.inputs.focus(function(e) {
    self.resetFocus();
    self.focusFieldset(jQuery(this).closest('fieldset'));
  });
  self.resetFocus = function() {
    self.fieldsets.parents('div:not(.aa-no-focus)').removeClass('active');
  };
  self.focusFieldset = function(fieldset) {
    fieldset.parents('div:not(.aa-no-focus)').addClass('active');
  };
};
jQuery.stripeTables = function(table) {
  jQuery('tbody tr', table)
      .hover(
          function() {
            jQuery(this).addClass('aa-hoverRow');
          },
          function() {
            jQuery(this).removeClass('aa-hoverRow');
          });
  jQuery('tbody tr:even', table).addClass('aa-altRow');
};
jQuery.tableToLinks = function(table, link) {
  jQuery('tbody tr', table).each(function(i, item) {
    var url = jQuery(link, item).attr('href');
    if (url !== undefined) {
      jQuery(item)
          .css('cursor', 'pointer')
          .hover(
              function() {
                jQuery(this).toggleClass('hover');
                jQuery(item).unbind('click');
                jQuery(item).bind('click', url, function(e) {
                  e.preventDefault();
                  window.location = e.data;
                });
              },
              function() {
                jQuery(this).toggleClass('hover');
              });
      jQuery('a', item).each(function(index) {
        var dealUrl = jQuery(link, item).attr('href');
        if (jQuery(this).attr('class') != jQuery(link, item).attr('class')) {
          jQuery(this).hover(
              function() {
                jQuery(item).toggleClass('hover');
                jQuery(item).unbind('click');
              },
              function() {
                jQuery(item).toggleClass('hover');
                jQuery(item).bind('click', dealUrl, function(e) {
                  e.preventDefault();
                  window.location = e.data;
                });
              });
        }
      });
    }
  });
};