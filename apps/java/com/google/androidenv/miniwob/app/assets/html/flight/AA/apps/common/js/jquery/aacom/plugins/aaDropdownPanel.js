(function($) {
var $dropdowns = $([]);
$(document).bind('click', function(e) {
  if (($(e.target).parents('[data-behavior~="dropdown"]').length === 0) &&
      (!$(e.target).is('[data-behavor~="dropdown-trigger"]'))) {
    $dropdowns.find('[data-behavior~="dropdown-panel"]:visible').hide();
    $dropdowns.find('[data-behavior~="dropdown-trigger"]:visible')
        .removeClass('is-active');
  }
  e.stopPropagation();
});
var methods = {
  init: function(options) {
    $dropdowns = $dropdowns.add(this);
    $dropdowns.find('[data-behavior~="dropdown-panel"]:visible').hide();
    var settings = $.extend({}, options);
    return this.each(function() {
      var $this = $(this);
      if (settings.width) {
        $this.find('[data-behavior~="dropdown-panel"]')
            .css('min-width', settings.width);
        $this.find('[data-behavior~="dropdown-panel"]')
            .css('width', settings.width);
      }
      if (settings.maxHeight) {
        $this.find('[data-behavior~="dropdown-panel"]')
            .css('max-height', settings.maxHeight);
      }
      if ($this.data('initialized')) {
        return;
      } else {
        $this.data('initialized', true);
      }
      var $trigger = $this.find('[data-behavior~="dropdown-trigger"]'),
          $panel = $this.find('[data-behavior~="dropdown-panel"]'),
          $close = $this.find('[data-behavior~="dropdown-close"]');
      $trigger.addClass('js-dropdown-trigger')
          .parents('[data-behavior~="dropdown-wrapper"]')
          .addClass('js-dropdown-wrapper')
          .parents('[data-behavior~="dropdown"]')
          .addClass('js-dropdown');
      $panel.addClass('js-dropdown-panel');
      $close.addClass('js-dropdown-close');
      $trigger.click(function(e) {
        e.stopPropagation();
        e.preventDefault();
        $dropdowns.not($this)
            .find('[data-behavior~="dropdown-panel"]:visible')
            .hide();
        $dropdowns.not($this)
            .find('[data-behavior~="dropdown-trigger"]')
            .removeClass('is-active');
        $trigger.toggleClass('is-active');
        $panel.toggle();
        $panel.find('a, input[type="text"], button, [tabindex=0], select')
            .filter(':visible')
            .first()
            .focus();
      });
      $close.click(function(e) {
        e.preventDefault();
        $this.find('[data-behavior~="dropdown-trigger"]')
            .removeClass('is-active');
        $this.find('[data-behavior~="dropdown-panel"]').hide();
      });
    });
  },
  show: function() {
    return this.each(function() {
      $(this).find('[data-behavior~="dropdown-panel"]:hidden').show();
    });
  },
  hide: function() {
    return this.each(function() {
      $(this).find('[data-behavior~="dropdown-panel"]:visible').hide();
    });
  },
  toggle: function() {
    return this.each(function() {
      $(this)
          .find('[data-behavior~="dropdown-panel"]')
          .toggle()
          .css('z-index', '9999');
      alert($(this).css('z-index'));
    });
  }
};
$.fn.dropdown = function(method) {
  if ($('html').hasClass('lt-ie8')) {
    return;
  }
  if (methods[method]) {
    return methods[method].apply(
        this, Array.prototype.slice.call(arguments, 1));
  } else {
    if (typeof method === 'object' || !method) {
      return methods.init.apply(this, arguments);
    } else {
      $.error('Method ' + method + ' does not exist on jQuery.dropdown');
    }
  }
};
})(jQuery);
jQuery(document).ready(function() {
  jQuery('[data-behavior~="dropdown"]').dropdown();
});