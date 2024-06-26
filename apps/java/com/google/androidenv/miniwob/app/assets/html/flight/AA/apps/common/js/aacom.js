function aaCustomInputs() {
  jQuery('label[data-behavior]').each(function() {
    var self = this;
    var _ = {};
    self.init = function() {
      _.label = jQuery(self);
      _.is_custombox = (_.label.is('[data-behavior~="custombox"]'));
      _.is_pillbox = (_.label.is('[data-behavior~="pillbox"]'));
      _.is_init = (_.label.is('[init~="true"]'));
      if (!_.is_custombox && !_.is_pillbox) {
        return;
      }
      _.input = jQuery('input[id="' + _.label.attr('for') + '"]');
      _.implicitLabel =
          _.label.find('input[id="' + _.label.attr('for') + '"]').length;
      _.initLabel();
      _.bindEvents();
    };
    _.initLabel = function() {
      if (_.is_init) {
        return;
      }
      if (_.implicitLabel > 0) {
        _.label.addClass('custombox-wrapper');
      } else {
        _.input.add(_.label).wrapAll('<div class="custombox-wrapper"></div>');
      }
      if (_.is_custombox) {
        _.label.addClass('custombox');
        if (_.label.find('div.control').length === 0) {
          _.label.prepend(
              '<div class="control ' + _.input.attr('type') + '"></div>');
        }
      }
      if (_.is_pillbox) {
        _.label.addClass('pillbox');
      }
    };
    _.bindEvents = function() {
      _.label.hover();
      _.input.bind('updateState', function() {
        _.input.is(':checked') ? _.label.addClass('selected') :
                                 _.label.removeClass('selected');
        _.input.is(':disabled') ? _.label.addClass('disabled') :
                                  _.label.removeClass('disabled');
      });
      _.input.trigger('updateState');
      _.input.change(function() {
        jQuery('input[name="' + jQuery(this).attr('name') + '"]')
            .trigger('updateState');
      });
      _.input.focus(function() {
        _.label.addClass('js-focus');
      });
      _.input.blur(function() {
        _.label.removeClass('js-focus');
      });
    };
    self.init();
  });
}
jQuery(document).ready(function() {
  aaCustomInputs();
});
(function($) {
$.fn.aaExpander = function(params) {
  var self = this, defaults = {
    expandText: 'More',
    collapseText: 'Less',
    triggerTemplate: $('<a class="icon-expand" href="#"></a>')
  },
      settings = $.extend({}, defaults, params);
  return this.each(function() {
    var expander = $(this), expanderTrigger = settings.triggerTemplate.clone(),
        expanderContent = expander.children(':eq(0)');
    expander.data(settings);
    if (expander.attr('data-expander-expandText')) {
      expander.data('expandText', expander.attr('data-expander-expandText'));
    }
    if (expander.attr('data-expander-collapseText')) {
      expander.data(
          'collapseText', expander.attr('data-expander-collapseText'));
    }
    expander.prepend(
        expanderTrigger.html('&nbsp;' + expander.data('expandText')));
    expanderContent.hide();
    expanderTrigger.on('click', function(e) {
      e.preventDefault();
      if (expander.hasClass('is-open')) {
        expanderContent.hide();
        expanderTrigger.html('&nbsp;' + expander.data('expandText'))
            .removeClass('icon-collapse')
            .addClass('icon-expand');
        expander.removeClass('is-open');
      } else {
        expanderTrigger.html('&nbsp;' + expander.data('collapseText'))
            .removeClass('icon-expand')
            .addClass('icon-collapse');
        expanderContent.show();
        expander.addClass('is-open');
      }
    });
  });
};
})(jQuery);
jQuery(document).ready(function() {
  jQuery('[data-behavior*="expander"]').aaExpander();
});
(function(jQuery) {
jQuery.fn.aaToggle = function() {
  var self = this;
  var onClick = function(ev) {
    var trigger = jQuery(this);
    var defaults = {
      expandText: 'Expand',
      collapseText: 'Collapse',
      animation: true
    };
    var settings = jQuery.extend({}, defaults, trigger.data());
    var href = (trigger.attr('href') != undefined) ?
        trigger.attr('href') :
        trigger.attr('data-toggle-href');
    var target = jQuery(href);
    if (target.length > 0) {
      trigger.find('i').toggleClass('icon-expand').toggleClass('icon-collapse');
      if (settings.animation) {
        target.stop().animate({height: 'toggle'}, 500);
      } else {
        target.toggle();
      }
    }
    ev.stopPropagation();
    ev.stopImmediatePropagation();
    return false;
  };
  jQuery(this.selector).live('click', onClick);
};
})(jQuery);
jQuery(document).ready(function() {
  jQuery(window).load(function() {
    jQuery('[data-behavior=toggle]').aaToggle();
  });
});
var aaTooltips = {};
var aaTooltip = function(elements, options) {
  return new (function() {
    var self = this;
    var _animate, _mouseEnter, _mouseLeave, _clickEvent, _fade, _ua, _jversion;
    self.initTooltip = function() {
      self.target = jQuery(elements);
      self.selector = self.target.selector;
      self.length = self.target.length;
      self.source = jQuery();
      self.isvisible = false;
      self.refresh = function() {
        self.target = jQuery(self.selector);
        self.length = self.target.length;
      };
      self.settings = jQuery.extend(
          {
            name: '',
            trigger: 'click',
            title: '',
            subtitle: '',
            text: '',
            html: '',
            htmlref: '',
            cssClass: '',
            width: '',
            height: '',
            position: 'auto',
            zIndex: 9999,
            showTitle: true,
            showClose: true,
            showArrow: true,
            animation: true,
            closeOnEscape: true,
            touchDevice: false,
            mobile: false,
            visible: true,
            onOpen: function() {},
            onClose: function() {},
            onBeforeOpen: function() {},
            onBeforeClose: function() {}
          },
          options || {});
      var _HTML =
          '<div class="aa-tooltip"><div class="tooltip-wrapper"><h5 class="tooltip-title"></h5><p class="tooltip-subtitle"></p><div class="tooltip-content"></div></div><div class="tooltip-arrow"><div class="tooltip-arrow-inner"></div></div><a href="#" class="tooltip-close" title="Close"><i class="icon-close icon-medium"></i></a></div>';
      self.tooltip = jQuery(_HTML);
      self.name = (self.settings.name != '') ? self.settings.name :
                                               _getSize(aaTooltips).toString();
      _ua = jQuery.browser;
      _ua.version = document.documentMode || _ua.version;
      _jversion = jQuery
                      .map(
                          jQuery.fn.jquery.split('.'),
                          function(i) {
                            return ('0' + i).slice(-2);
                          })
                      .join('.');
      _mouseEnter = (_jversion < '01.04') ? 'mouseover' : 'mouseenter';
      _mouseLeave = (_jversion < '01.04') ? 'mouseout' : 'mouseleave';
      _clickEvent = (self.settings.touchDevice) ? 'touchstart' : 'click';
      _fade = !(_ua.msie && _ua.version <= 8);
      _animate = true;
      if (self.settings.width == '' && document.compatMode == 'BackCompat' &&
          _ua.msie) {
        self.settings.width = '300';
      }
      _bindOpenEvent();
      _bindFocusEvent();
      _bindDocumentEvent();
      _bindKeydownEvent();
      if (self.settings.touchDevice) {
        _bindOrientationChangeEvent();
      } else {
        _bindResizeEvent();
      }
    };
    self.openTooltip = function(source) {
      self.refresh();
      if (self.target.length == 0) {
        return false;
      }
      if (!_settings('visible')) {
        return false;
      }
      if (source == undefined) {
        animate = false;
        source = self.target.filter(':first');
      }
      self.removeTooltip();
      self.source = jQuery(source).filter(':first');
      var _title = _settings('title');
      var _subtitle = _settings('subtitle');
      var _text = _settings('text');
      var _htmlref = _settings('htmlref');
      var _html = (_htmlref != '' && jQuery(_htmlref).length > 0) ?
          jQuery(_htmlref).html() :
          self.settings.html;
      var _content = (_html != '') ? _html : _text;
      if (_title == '' && _subtitle == '' && _content == '') {
        return false;
      }
      self.tooltip.removeAttr('style');
      self.tooltip.find('*').removeAttr('style');
      if (!_settings('showTitle') || _title == '') {
        self.tooltip.find('.tooltip-title').hide();
      }
      if (_subtitle == '') {
        self.tooltip.find('.tooltip-subtitle').hide();
      }
      if (_content == '') {
        self.tooltip.find('.tooltip-content').hide();
      }
      if (!_settings('showClose')) {
        self.tooltip.find('.tooltip-close').hide();
      }
      if (!_settings('showArrow')) {
        self.tooltip.find('.tooltip-arrow').hide();
      }
      if (_settings('cssClass') != '') {
        self.tooltip.addClass(_settings('cssClass'));
      }
      if (_settings('width') != '') {
        self.tooltip.css('width', _settings('width'));
      }
      if (_settings('height') != '') {
        self.tooltip.css('height', _settings('height'));
      }
      if (_settings('zIndex') > 0) {
        self.tooltip.css('z-index', _settings('zIndex'));
      }
      if (_fade) {
        self.tooltip.css('opacity', 0);
      }
      self.tooltip.find('.tooltip-title').html(_title);
      self.tooltip.find('.tooltip-subtitle').html(_subtitle);
      self.tooltip.find('.tooltip-content').html(_content);
      self.tooltip.find('.tooltip-text').html(_text);
      var _result = self.settings.onBeforeOpen(self);
      if (_result == false) {
        return _result;
      }
      self.tooltip.appendTo('body');
      _renderTooltip(self.source);
      _bindHoverEvent();
      _bindClickEvent();
      self.settings.onOpen(self);
    };
    self.closeTooltip = function() {
      if (self.target.length == 0) {
        return false;
      }
      if (!self.tooltip.is(':visible')) {
        return false;
      }
      _result = self.settings.onBeforeClose(self);
      if (_result == false) {
        return _result;
      }
      if (_settings('animation')) {
        var _top = (self.tooltip.hasClass('top')) ? '+=10' : '-=10';
        _animateTooltip(_top, 0, 200, function() {
          jQuery(this).remove();
        });
      } else {
        self.tooltip.remove();
      }
      self.settings.onClose(self);
      self.source = jQuery();
      self.isvisible = false;
    };
    self.removeTooltip = function() {
      if (self.target.length == 0) {
        return false;
      }
      if (!self.tooltip.is(':visible')) {
        return false;
      }
      self.tooltip.remove();
      self.source = jQuery();
      self.isvisible = false;
    };
    var _settings = function(name) {
      var _s = self.settings[name];
      var _v = self.source.attr('data-tooltip-' + name) || _s;
      if (typeof (_s) == 'boolean') {
        _v = (String(_v).toLowerCase() == 'true');
      }
      if (typeof (_s) == 'number') {
        _v = parseInt(_v);
      }
      return _v;
    };
    var _bindOpenEvent = function() {
      if (self.settings.trigger == 'hover' ||
          self.settings.trigger == 'click') {
        var triggerEvent = (self.settings.trigger == 'hover') ?
            _mouseEnter :
            self.settings.trigger;
        self.target.live(triggerEvent, function() {
          self.openTooltip(this);
        });
      }
    };
    var _bindFocusEvent = function() {
      if (self.settings.trigger == 'click') {
        var textInput = self.target.find(':input');
        textInput.live('click', function(ev) {
          ev.stopPropagation();
        });
        textInput.live('focus', function() {
          var source = jQuery(this).parents('[data-behavior]:first');
          self.openTooltip(source);
        });
        textInput.live('blur', function() {
          self.closeTooltip();
        });
      }
    };
    var _bindDocumentEvent = function() {
      if (self.settings.trigger == 'click') {
        self.target.live(_clickEvent, function(ev) {
          return _stopEventPropagation(ev);
        });
      }
      jQuery(document).bind(_clickEvent, function(e) {
        self.closeTooltip();
      });
    };
    var _bindKeydownEvent = function() {
      if (self.settings.closeOnEscape) {
        var escKey = 27;
        jQuery(document).bind('keydown', function(ev) {
          if (ev.keyCode == escKey) {
            self.closeTooltip();
          }
        });
      }
    };
    var _bindResizeEvent = function() {
      jQuery(window).bind('resize', function(e) {
        self.closeTooltip();
      });
    };
    var _bindOrientationChangeEvent = function() {
      jQuery(window).bind('orientationchange', function() {
        self.removeTooltip();
      });
    };
    var _stopEventPropagation = function(ev) {
      ev.stopPropagation();
      ev.stopImmediatePropagation();
      if (self.settings.touchDevice) {
        return;
      }
      return false;
    };
    var _bindHoverEvent = function() {
      if (self.settings.trigger == 'hover') {
        self.tooltip.find('.tooltip-close').hide();
        self.target.live(_mouseLeave, function() {
          self.closeTooltip();
        });
      }
    };
    var _bindClickEvent = function() {
      if (self.settings.trigger == 'click') {
        self.tooltip.find('.tooltip-title').css({paddingRight: '20px'});
        self.tooltip.find('.tooltip-close').show();
        self.tooltip.find('.tooltip-close').bind('click', function(ev) {
          self.closeTooltip();
          return false;
        });
        self.tooltip.bind(_clickEvent, function(ev) {
          return _stopEventPropagation(ev);
        });
      }
    };
    var _renderTooltip = function(target) {
      if (self.target.length == 0) {
        return false;
      }
      var pos_left = target.offset().left + (target.outerWidth() / 2) -
          (self.tooltip.outerWidth() / 2);
      var pos_top = _getPosTop(target) - self.tooltip.outerHeight() - 25;
      var browserWidth = jQuery(window).width();
      var maxWidth = self.tooltip.outerWidth() + self.tooltip.outerWidth() / 2;
      var smallWindow = (maxWidth > browserWidth) ? true : false;
      pos_left = _initializePositionLeft(pos_left, smallWindow, target);
      pos_left = _initializePositionRight(pos_left, browserWidth, target);
      pos_top = _initializePositionTop(pos_top, target);
      if (smallWindow) {
        var arrow_posLeft = (self.tooltip.hasClass('right')) ?
            target.offset().left - pos_left - 3 :
            target.offset().left - pos_left + 5;
        self.tooltip.find('.tooltip-arrow').css('left', arrow_posLeft);
      } else {
        self.tooltip.find('.tooltip-arrow').css('left', '');
      }
      self.tooltip.css({left: pos_left, top: pos_top});
      if (_settings('animation') && _animate) {
        var _top = (self.tooltip.hasClass('top')) ? '-=10' : '+=10';
        _animateTooltip(_top, 1, 300);
      } else {
        var _top = (self.tooltip.hasClass('top')) ? pos_top - 10 : pos_top + 10;
        self.tooltip.css({top: _top});
        if (_fade) {
          self.tooltip.css({opacity: 1});
        }
        self.tooltip.show();
      }
      _animate = true;
      self.isvisible = true;
    };
    var _animateTooltip = function(_top, _opacity, _delay, _callback) {
      if (_callback == undefined) {
        _callback = function() {};
      }
      if (_fade) {
        self.tooltip.stop(true).animate(
            {top: _top, opacity: _opacity}, _delay, _callback);
      } else {
        self.tooltip.stop(true).animate({top: _top}, _delay, _callback);
      }
    };
    var _initializePositionLeft = function(pos_left, smallWindow, target) {
      if (pos_left < 0) {
        if (!smallWindow) {
          pos_left = target.offset().left + target.outerWidth() / 2 - 14;
          self.tooltip.addClass('left');
        } else {
          pos_left = 7;
        }
      } else {
        self.tooltip.removeClass('left');
      }
      return pos_left;
    };
    var _initializePositionRight = function(pos_left, browserWidth, target) {
      if (pos_left + self.tooltip.outerWidth() > browserWidth) {
        pos_left = target.offset().left - self.tooltip.outerWidth() +
            target.outerWidth() / 2 + 10;
        if (pos_left < 0) {
          pos_left = 8;
        }
        self.tooltip.addClass('right');
      } else {
        self.tooltip.removeClass('right');
      }
      return pos_left;
    };
    var _initializePositionTop = function(pos_top, target) {
      var belowTarget = false;
      if (_settings('position') == '' || _settings('position') == 'auto') {
        if ((pos_top < 0) || (pos_top < _getScrollTop())) {
          belowTarget = true;
        }
      } else {
        if (_settings('position') == 'below') {
          belowTarget = true;
        }
      }
      if (belowTarget) {
        pos_top = _getPosTop(target) + target.outerHeight() + 25;
        self.tooltip.addClass('top');
      } else {
        self.tooltip.removeClass('top');
      }
      return pos_top;
    };
    var _getScrollTop = function() {
      var _scrolltop = jQuery(document).scrollTop();
      if (_ua.msie && _ua.version <= 8 && _jversion <= '01.04') {
        _scrolltop = jQuery(document.documentElement).scrollTop();
      }
      return _scrolltop;
    };
    var _getPosTop = function(target) {
      var _top = target.offset().top;
      if (_ua.msie && _ua.version <= 8 && _jversion <= '01.04') {
        _top += jQuery(document.documentElement).scrollTop();
      }
      return _top;
    };
    var _getSize = function(object) {
      var size = 0;
      for (var x in object) {
        size++;
      }
      return size;
    };
    self.initTooltip();
  });
};
(function(JQuery) {
jQuery.fn.aaTooltip = function(options) {
  var tooltip = aaTooltip(this, options);
  if (aaTooltips != undefined && tooltip.name != undefined &&
      tooltip.name != '') {
    aaTooltips[tooltip.name] = tooltip;
  }
  return tooltip;
};
})(jQuery);
jQuery(document).ready(function() {
  jQuery(window).load(function() {
    jQuery('[data-behavior=tooltip]').aaTooltip({name: 'default'});
    jQuery('[data-behavior=tooltip-auto]')
        .aaTooltip({name: 'default-auto', width: 'auto'});
    jQuery('[data-behavior=tooltip-warning]')
        .aaTooltip(
            {name: 'default-warning', cssClass: 'warning', title: 'Warning'});
    jQuery('[data-behavior=tooltip-error]')
        .aaTooltip({name: 'default-error', cssClass: 'error'});
    jQuery('[data-behavior=tooltip-success]')
        .aaTooltip({name: 'default-success', cssClass: 'success'});
  });
  jQuery('[data-behavior=popover]').each(function() {
    var toolTipId = jQuery(this).attr('id');
    var toolTiphref = jQuery(this).attr('href');
    jQuery('#' + toolTipId).aaTooltip({
      name: toolTipId,
      trigger: 'click',
      html: jQuery(toolTiphref).html(),
      onBeforeOpen: function() {
        jQuery('.aa-tooltip').remove();
      },
      onOpen: function() {
        jQuery('.aa-tooltip a.aa-pop-win-med').aaGenericPopup('MEDIUM');
      }
    });
  });
});
(function($) {
jQuery.fn.aaBusy = function(options) {
  var self = {},
      defaults = {message: '', showlogo: true, position: undefined, form: ''};
  self.settings = $.extend({}, defaults, options);
  self.source = this;
  self.start = function() {
    var message,
        $this = jQuery(self.source).filter(':first'),
        $module = $this.find('> .aa-busy-module'),
        $form = jQuery(self.settings.form),
        $obj = jQuery(
            '<div class="aa-busy-module"><div class="aa-busy-bg"></div><div class="aa-busy-img"><div><img alt="American Airlines" class="aa-busy-logo" src="content/images/chrome/rebrand/aa-flight-icon.png"></div><p><span class="aa-busy-text"></span></p><span class="aa-busy-spinner" aria-hidden="true"></span></div></div>'),
        condition = ($this.length > 0 && $module.length === 0);
    if (condition) {
      $this.addClass('aa-busy');
      $this.addClass('is-busy');
      message = $this.attr('data-busy-message') || self.settings.message;
      if (message !== '') {
        $obj.find('.aa-busy-text').html(message);
      } else {
        $obj.find('.aa-busy-text').remove();
      }
      if (!self.settings.showlogo) {
        $obj.find('.aa-busy-logo').remove();
      }
      $this.append($obj);
      var a = $this.find('.aa-busy-module').outerHeight(),
          b = $this.find('.aa-busy-img').outerHeight(),
          calc = ((a - b) / (2 * a)) * 100,
          pos = $this.data('busy-position') || self.settings.position ||
          calc + '%';
      $this.find('.aa-busy-img').css('top', pos);
      $this.find('.aa-busy-text').attr('tabindex', -1).focus();
      if ($form.length > 0) {
        setTimeout(function() {
          $form.submit();
        }, 500);
        jQuery(window).unload(function() {});
      }
    }
    return condition;
  };
  self.stop = function() {
    var $this = jQuery(self.source).filter(':first'),
        $module = $this.find('> .aa-busy-module'),
        condition = ($this.length > 0 && $module.length > 0);
    if (condition) {
      $module.animate({opacity: 'hide'}, 500, function() {
        $module.remove();
        $this.removeClass('aa-busy');
        $this.removeClass('is-busy');
        if (jQuery('*:focus').length === 0 && $this.hasClass('ui-dialog')) {
          $this.find('h2').focus();
        }
      });
    }
    return condition;
  };
  return self;
};
})(jQuery);
jQuery.fn.serializeObject = function() {
  var o = {};
  var a = this.serializeArray();
  jQuery.each(a, function() {
    if (o[this.name]) {
      if (!o[this.name].push) {
        o[this.name] = [o[this.name]];
      }
      o[this.name].push(this.value || '');
    } else {
      o[this.name] = this.value || '';
    }
  });
  return o;
};
