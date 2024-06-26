var $device = {
  mobile: false,
  tablet: false,
  desktop: true,
  touch: false,
  responsive: false,
  init: function() {
    this.desktop = (!this.tablet && !this.mobile);
    this.touch = (this.tablet || this.mobile);
    if (this.tablet) {
      jQuery('html').addClass('is-tablet');
    }
    if (this.mobile) {
      jQuery('html').addClass('is-mobile');
    }
    if (this.responsive) {
      jQuery('html').addClass('is-responsive');
    }
  },
  viewport: function() {
    if (this.responsive) {
      var check = function(css) {
        if (jQuery('.' + css).length == 0) {
          jQuery('body').append('<div class="' + css + '"></div>');
        }
        return (jQuery('.' + css).css('display') != 'none');
      };
      if (check('visible-phone')) {
        return 'phone';
      }
      if (check('visible-tablet')) {
        return 'tablet';
      }
    }
    return 'desktop';
  },
  landscape: function() {
    return (jQuery(window).height() < jQuery(window).width());
  }
};