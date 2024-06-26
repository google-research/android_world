var activeDialog = '';
var dialogArray = {};
var dialogLinkObj;
function aa_Utilities() {
  this.aaDialog = function(name, attributes) {
    return new aa_Utilities_Dialog(name, attributes);
  };
  this.aaFormat = new aa_Utilities_Format();
}
function aa_Utilities_Dialog(dialog, props) {
  var self = this;
  var dialogObj = '', dialogName = '';
  if (dialog !== undefined) {
    if (typeof (dialog) == 'object') {
      if (dialog.attr('id') !== undefined) {
        dialogObj = '#' + dialog.attr('id');
        dialogName = dialog.attr('id');
      }
    } else {
      if (typeof (dialog) == 'string') {
        if (dialog.indexOf('#') === 0) {
          dialogObj = dialog;
          dialogName = dialog.replace(/#/, '');
        } else {
          dialogObj = '#' + dialog + 'Dialog';
          dialogName = dialog;
        }
      }
    }
  }
  var dialogObjTitle = '#' + dialogName + 'Title';
  var dialogLink = '.aa-dialog-' + dialogName;
  var wrapperClass = 'aa-dialog-content-wrapper';
  self.version = 2.1;
  self.jQueryUIVersion = jQuery
                             .map(
                                 jQuery.ui.version.split('.'),
                                 function(i) {
                                   return ('0' + i).slice(-2);
                                 })
                             .join('.');
  self.initDialog = function() {
    props = (props !== undefined) ? props : {};
    props.hide = (props.hide !== undefined) ? props.hide : null;
    props.width = (props.width !== undefined) ? props.width : 882;
    props.width = (props.width == 'small') ?
        582 :
        ((props.width == 'medium') ?
             840 :
             ((props.width == 'large') ? 926 : props.width));
    props.height = (props.height !== undefined) ? props.height : 'auto';
    props.maxHeight = (props.maxHeight !== undefined) ? props.maxHeight : 600;
    props.minHeight = (props.minHeight !== undefined) ? props.minHeight : 150;
    props.modal = (props.modal !== undefined) ? props.modal : true;
    props.overlay = (props.overlay !== undefined) ? props.overlay : true;
    props.cssClass = (props.cssClass !== undefined) ? props.cssClass : '';
    props.showClose = (props.showClose !== undefined) ? props.showClose : true;
    props.showTitle = (props.showTitle !== undefined) ? props.showTitle : true;
    props.showBusy = (props.showBusy !== undefined) ? props.showBusy : false;
    props.quickflip = (props.quickflip !== undefined) ? props.quickflip : false;
    props.buttons = (props.buttons !== undefined) ? props.buttons : [];
    props.toggleScroll =
        (props.toggleScroll !== undefined) ? props.toggleScroll : false;
    props.zIndex = (props.zIndex !== undefined) ? props.zIndex : 1000;
    props.closeOnEscape =
        (props.closeOnEscape !== undefined) ? props.closeOnEscape : true;
    props.submitOnEnter =
        (props.submitOnEnter !== undefined) ? props.submitOnEnter : false;
    props.title = (props.title !== undefined) ?
        props.title :
        jQuery(dialogObjTitle).attr('value') || jQuery(dialogObjTitle).html();
    props.position = (props.position !== undefined) ? props.position : 'center';
    props.adaptive = (props.adaptive !== undefined) ? props.adaptive : true;
    props.onOpen = (props.onOpen !== undefined) ? props.onOpen : function() {};
    props.onClose =
        (props.onClose !== undefined) ? props.onClose : function() {};
    props.onBeforeOpen =
        (props.onBeforeOpen !== undefined) ? props.onBeforeOpen : function() {};
    props.onBeforeClose = (props.onBeforeClose !== undefined) ?
        props.onBeforeClose :
        function() {};
    props.btnPaneContent = (props.btnPaneContent !== undefined) ?
        props.btnPaneContent :
        jQuery(dialogObj).find('#' + dialogName + 'BtnPaneContent').html();
    props.titlePaneContent = (props.titlePaneContent !== undefined) ?
        props.titlePaneContent :
        jQuery(dialogObj).find('#' + dialogName + 'TitlePaneContent').html();
    props.resizable = (props.resizable !== undefined) ? props.resizable : true;
    props.aaPosition = jQuery.extend(
        {vertical: null, horizontal: null, of: null}, props.aaPosition);
    dialogArray[dialogObj] = props;
    var resizable = false;
    var draggable = (props.modal) ? false : true;
    jQuery(dialogObj).addClass('aa-dialog-content-pad');
    if (jQuery(dialogObj).find('.' + wrapperClass).length === 0) {
      jQuery(dialogObj).html(
          '<div class="' + wrapperClass + '">' + jQuery(dialogObj).html() +
          '</div>');
    }
    if (props.quickflip) {
      jQuery(dialogObj + ' .quickFlip-wrapper')
          .css({width: props.width - 60, height: 'auto'});
      jQuery(dialogObj + ' .quickFlip-wrapper').quickFlip({noResize: true});
      jQuery('.ui-dialog .quickFlip-firstPanel').live('click', function() {
        setFlipPanel(0, true);
        return false;
      });
      jQuery('.ui-dialog .quickFlip-secondPanel').live('click', function() {
        setFlipPanel(1, true);
        return false;
      });
      jQuery('.ui-dialog .quickFlip-thirdPanel').live('click', function() {
        setFlipPanel(2, true);
        return false;
      });
    }
    jQuery(dialogObj).dialog({
      autoOpen: false,
      modal: props.modal,
      draggable: draggable,
      resizable: resizable,
      bgiframe: true,
      title: props.title,
      width: props.width,
      height: props.height,
      minHeight: props.minHeight,
      zIndex: props.zIndex,
      closeOnEscape: props.closeOnEscape,
      open: props.onOpen,
      close: props.onClose,
      closeText: '',
      beforeClose: props.onBeforeClose
    });
    if (props.buttons.length > 0) {
      var btnsArray = {};
      var btnsClass =
          'jQuery(dialogObj).parents(\'.ui-dialog\').find(\'.ui-dialog-buttonpane button\')';
      var btnsClick = btnsClass;
      for (var i = 0; i < props.buttons.length; i++) {
        var btn = props.buttons[i];
        btn.name = (btn.name !== undefined) ? btn.name : 'OK';
        btn.callback =
            (btn.callback !== undefined) ? btn.callback : function() {};
        btn.cssClass =
            (btn.cssClass !== undefined) ? btn.cssClass : 'aa-btn-primary';
        btn.closeDialog =
            (btn.closeDialog !== undefined) ? btn.closeDialog : true;
        btn.hideOnpanel =
            (btn.hideOnpanel !== undefined) ? ',' + btn.hideOnpanel + ',' : '';
        btn.id =
            (btn.id !== undefined) ? btn.id : dialogName + 'DialogButton' + i;
        btnsArray[btn.name] = btn.callback;
        btnsClass += '.eq(' + i + ').attr(\'id\', \'' + btn.id +
            '\').attr(\'class\', \'aa-btn ' + btn.cssClass +
            '\').removeAttr(\'role\').hover(function(){jQuery(this).removeClass(\'ui-state-hover\')}).focus(function(){jQuery(this).removeClass(\'ui-state-focus\')}).mousedown(function(){jQuery(this).removeClass(\'ui-state-active\')}).keypress(function(){jQuery(this).removeClass(\'ui-state-active\')}).end()';
        if (btn.closeDialog) {
          btnsClick += '.eq(' + i +
              ').click(function(){jQuery(dialogObj).dialog(\'close\'); return false;}).end()';
        }
      }
      jQuery(dialogObj).dialog('option', 'buttons', btnsArray);
      eval(btnsClick);
      eval(btnsClass);
      if (props.btnPaneContent !== undefined && props.btnPaneContent.length) {
        jQuery(dialogObj)
            .parents('.ui-dialog')
            .find('.ui-dialog-buttonpane')
            .prepend(props.btnPaneContent);
      }
    }
    self.initTitleBar(dialogObj, props);
    if (props.toggleScroll) {
      jQuery(dialogObj).bind('dialogclose', function() {
        jQuery('body').css('overflow', 'auto');
      });
    }
    jQuery(dialogObj).bind('dialogclose', _closeDialog);
    if (props.submitOnEnter) {
      jQuery(dialogObj + ' form input').live('keydown', function(e) {
        var keyCode = e.keyCode || e.which;
        if (keyCode == 13) {
          jQuery(this).parents('form:first').submit();
        }
      });
    }
    jQuery(dialogLink).live('click', function() {
      self.openDialog(this);
      return false;
    });
  };
  self.initTitleBar = function(dialogObj, props) {
    var $titleBar = jQuery(dialogObj)
                        .parents('.ui-dialog:first')
                        .find('.ui-dialog-titlebar');
    var $dialogTitle = $titleBar.find('.ui-dialog-title');
    $dialogTitle.appendTo($dialogTitle.parent());
    $dialogTitle.replaceWith(
        '<h2 tabindex="0" id="' + $dialogTitle.attr('id') + '" class="' +
        $dialogTitle.attr('class') + '">' + $dialogTitle.html() + '</h2>');
    $dialogTitle.css('margin', '2px');
    self.initCloseIcon($titleBar);
    if (props.showTitle && (props.titlePaneContent !== undefined) &&
        (props.titlePaneContent.length > 0)) {
      $titleBar.append(props.titlePaneContent);
    }
  };
  self.initCloseIcon = function($titleBar) {
    var closeText = (typeof (AAcom) !== 'undefined') ?
        AAcom.prototype.getProperty('dialog.closeText') :
        'Close window';
    var $closeTag = $titleBar.find('.ui-dialog-titlebar-close');
    var $closeIconHiddenText = $closeTag.find('.ui-button-text');
    var $closeIconTag = $closeTag.find('.ui-icon');
    $closeIconHiddenText.text(closeText);
    $closeIconTag.text('');
    if ($closeIconHiddenText.length === 0) {
      $closeTag.append(
          '<span class="ui-button-text hidden-accessible">' + closeText +
          '</span>');
    }
    $closeTag.attr('id', dialogName + 'DialogClose');
  };
  self.openDialog = function(clickObj) {
    if (dialogObj.length <= 0) {
      return false;
    }
    if (activeDialog !== '' && activeDialog != dialogObj) {
      if (jQuery(activeDialog).dialog('isOpen')) {
        jQuery(activeDialog).dialog('close');
      }
    }
    activeDialog = dialogObj;
    if (jQuery(dialogObj).dialog('isOpen')) {
      jQuery(dialogObj).dialog('close');
    }
    dialogLinkObj = clickObj;
    var _position = (props.adaptive && is_phone()) ? 'absolute' : 'fixed';
    jQuery(dialogObj).parent('.ui-dialog:first').addClass(props.cssClass);
    jQuery(dialogObj).parent().css('position', _position);
    jQuery(dialogObj).css('position', 'relative');
    jQuery(dialogObj).dialog('option', 'position', props.position);
    props.onBeforeOpen(clickObj);
    jQuery(dialogObj).dialog('open');
    self.resizeDialog();
    var $wrapper = jQuery(activeDialog + ' .' + wrapperClass);
    if ($wrapper.find(':input,a,[tabindex=0]').filter(':visible').length ===
        0) {
      $wrapper.attr('tabindex', '0');
    }
    if (props.quickflip && clickObj !== undefined) {
      if (jQuery(clickObj).hasClass('quickFlip-secondPanel')) {
        setFlipPanel(1, false);
      } else {
        if (jQuery(clickObj).hasClass('quickFlip-thirdPanel')) {
          setFlipPanel(2, false);
        } else {
          setFlipPanel(0, false);
        }
      }
    }
    if (!props.overlay) {
      jQuery('.ui-widget-overlay').css('background', 'none');
    }
    if (props.adaptive && is_phone()) {
      jQuery(dialogObj).parent('.ui-dialog:first').css('top', getPositionTop());
    }
    if (props.showClose !== null && !props.showClose) {
      jQuery(dialogObj)
          .parents('.ui-dialog:first')
          .find('.ui-dialog-titlebar-close')
          .remove();
    }
    if (props.showTitle !== null && !props.showTitle) {
      jQuery(dialogObj)
          .parents('.ui-dialog:first')
          .find('.ui-dialog-titlebar')
          .remove();
    }
    if (props.showBusy !== null && props.showBusy) {
      self.busyStart('Loading...');
    }
    jQuery(window).on('resize.aaDialog', self.resizeDialog);
    var elemObj = props.aaPosition.of ? props.aaPosition.of : dialogObj;
    jQuery(elemObj).scrollTop(0);
    self.setFocus();
  };
  self.setFocus = function() {
    var $dialog = jQuery(activeDialog).parents('.ui-dialog:first'),
        $dialogTitle = $dialog.find('.ui-dialog-title');
    if ($dialogTitle) {
      $dialogTitle.focus();
    } else {
      $dialog.focus();
    }
  };
  self.closeDialog = function() {
    if (dialogObj.length <= 0) {
      return false;
    }
    if (jQuery(dialogObj).dialog('isOpen')) {
      jQuery(dialogObj).dialog('close');
    }
  };
  var _closeDialog = function(ev) {
    activeDialog = '';
    if (self.jQueryUIVersion < '01.10' && jQuery(dialogLinkObj).length > 0) {
      setTimeout(function() {
        jQuery(dialogLinkObj).focus();
        dialogLinkObj = undefined;
      }, 200);
    }
    ev.stopPropagation();
    ev.stopImmediatePropagation();
    return false;
  };
  self.busyStart = function(busyMsg) {
    if (activeDialog.length <= 0) {
      return false;
    }
    var uiParent = jQuery(activeDialog).parents('.ui-dialog:first');
    var uiBusy = uiParent.find('> .aa-busy-module');
    uiParent.addClass('aa-busy');
    if (busyMsg === undefined) {
      busyMsg = '';
    }
    if (uiBusy.length === 0) {
      uiParent.append(
          '<div class="aa-busy-module"><div class="aa-busy-bg"></div><div class="aa-busy-img"><i class="spinner"></i><span class="text"></span></div></div>');
      uiBusy = uiParent.find('> .aa-busy-module');
    }
    if (uiBusy.length == 1) {
      uiBusy.find('span').html(busyMsg);
    }
  };
  self.busyStop = function() {
    if (activeDialog.length <= 0) {
      return false;
    }
    var uiParent = jQuery(activeDialog).parents('.ui-dialog:first');
    var uiBusy = uiParent.find('> .aa-busy-module');
    if (uiBusy.length == 1) {
      uiBusy.animate({opacity: 'hide'}, 500, function() {
        uiBusy.remove();
        uiParent.removeClass('aa-busy');
      });
      jQuery(window).resize();
    }
  };
  self.resizeDialog = function(options) {
    if (activeDialog.length <= 0 || !isResizeEnable()) {
      return false;
    }
    var activeDialProps = dialogArray[activeDialog];
    var settings = jQuery.extend(
        {
          width: activeDialProps.width,
          height: activeDialProps.height,
          maxHeight: (activeDialProps.adaptive && is_phone()) ?
              '' :
              activeDialProps.maxHeight
        },
        options);
    var newHeight = settings.height;
    var newWidth = settings.width;
    var maxHeight = settings.maxHeight;
    var paddingTop = parseInt(jQuery(activeDialog).parent().css('padding-top'));
    var paddingBottom =
        parseInt(jQuery(activeDialog).parent().css('padding-bottom'));
    var paddingLeft = parseInt(jQuery(activeDialog).css('padding-left'));
    var paddingRight = parseInt(jQuery(activeDialog).css('padding-right'));
    var marginLeft = parseInt(jQuery(activeDialog).css('margin-left'));
    var marginRight = parseInt(jQuery(activeDialog).css('margin-right'));
    var titleBar = jQuery(activeDialog)
                       .parents('.ui-dialog:first')
                       .find('.ui-dialog-titlebar:visible');
    var buttonBar = jQuery(activeDialog)
                        .parents('.ui-dialog:first')
                        .find('.ui-dialog-buttonpane:visible');
    if (newHeight != 'auto') {
      if (titleBar.length > 0) {
        newHeight -= titleBar.outerHeight();
      }
      if (buttonBar.length > 0) {
        newHeight -= buttonBar.outerHeight();
      }
      newHeight -= paddingTop + paddingBottom;
    }
    jQuery(activeDialog).css('height', newHeight);
    jQuery(activeDialog).css('max-height', maxHeight);
    if (jQuery(window).height() <=
        jQuery(activeDialog).parent().outerHeight()) {
      if (!(activeDialProps.adaptive && is_phone())) {
        var totalHeight = jQuery(window).height();
        if (titleBar.length > 0) {
          totalHeight -= titleBar.outerHeight();
        }
        if (buttonBar.length > 0) {
          totalHeight -= buttonBar.outerHeight();
        }
        totalHeight -= paddingTop + paddingBottom;
        jQuery(activeDialog).css('height', totalHeight * 0.8);
        jQuery(activeDialog).css('max-height', totalHeight * 0.8);
      }
    }
    if (activeDialProps.toggleScroll) {
      var _overflow =
          (activeDialProps.adaptive && is_phone()) ? 'auto' : 'hidden';
      jQuery('body').css('overflow', _overflow);
    }
    jQuery(activeDialog).css('width', 'auto');
    jQuery(activeDialog).css('max-width', activeDialProps.width);
    jQuery(activeDialog + ' .' + wrapperClass)
        .css({'padding-right': 0, position: 'relative', margin: '2px'});
    jQuery(activeDialog).parent().css('width', activeDialProps.width);
    jQuery(activeDialog).parent().css('max-width', activeDialProps.width);
    if (jQuery(window).width() <= jQuery(activeDialog).parent().outerWidth()) {
      var scrollbarWidth = 20;
      newWidth -= paddingLeft + paddingRight + marginLeft + marginRight +
          scrollbarWidth;
      jQuery(activeDialog + ' .' + wrapperClass).css({
        width: newWidth,
        'padding-right': paddingRight,
        position: 'relative'
      });
      jQuery(activeDialog).parent().css('width', jQuery(window).width() * 0.95);
      jQuery(activeDialog)
          .parent()
          .css('max-width', jQuery(window).width() * 0.95);
    } else {
      jQuery(activeDialog + ' .' + wrapperClass).css({width: ''});
    }
    jQuery(activeDialog).dialog('option', 'position', activeDialProps.position);
    if (activeDialProps.adaptive && is_phone()) {
      jQuery(activeDialog)
          .parent('.ui-dialog:first')
          .css('top', jQuery(window).scrollTop() + 10);
    }
  };
  var setFlipPanel = function(index, animation) {
    if (activeDialog.length <= 0) {
      return false;
    }
    var activeDialProps = dialogArray[activeDialog];
    var panelHeight = activeDialProps.height;
    if (index === 0) {
      panelHeight = jQuery(activeDialog).height() -
          jQuery(activeDialog + ' .quickFlip-wrapper .first-flipPanel')
              .height();
    } else {
      if (index == 1) {
        panelHeight = jQuery(activeDialog).height() -
            jQuery(activeDialog + ' .quickFlip-wrapper .second-flipPanel')
                .height();
      } else {
        if (index == 2) {
          panelHeight = jQuery(activeDialog).height() -
              jQuery(activeDialog + ' .quickFlip-wrapper .third-flipPanel')
                  .height();
        }
      }
    }
    var flipSpeed = (animation) ? 200 : 0;
    var flipWidth = (panelHeight > 0) ? activeDialProps.width - 60 :
                                        activeDialProps.width - 77;
    jQuery(activeDialog + ' .quickFlip-wrapper')
        .css('width', flipWidth)
        .css('height', 'auto');
    jQuery(activeDialog + ' .quickFlip-wrapper')
        .quickFlipper(
            {
              noResize: true,
              closeSpeed: flipSpeed,
              openSpeed: flipSpeed,
              refresh: true,
              panelWidth: flipWidth
            },
            index);
    jQuery(activeDialog + ' .quickFlip-wrapper .first-flipPanel')
        .css({height: 'auto', 'padding-bottom': '30px'});
    jQuery(activeDialog + ' .quickFlip-wrapper .second-flipPanel')
        .css({height: 'auto', 'padding-bottom': '30px'});
    jQuery(activeDialog + ' .quickFlip-wrapper .third-flipPanel')
        .css({height: 'auto', 'padding-bottom': '30px'});
    jQuery(activeDialog).scrollTop(0);
    if (activeDialProps.buttons.length > 0) {
      for (var i = 0; i < activeDialProps.buttons.length; i++) {
        jQuery(activeDialog)
            .parents('.ui-dialog')
            .find('.ui-dialog-buttonpane button')
            .eq(i)
            .show();
        if (activeDialProps.buttons[i].hideOnpanel.indexOf(',' + index + ',') >=
            0) {
          jQuery(activeDialog)
              .parents('.ui-dialog')
              .find('.ui-dialog-buttonpane button')
              .eq(i)
              .hide();
        }
      }
    }
  };
  var is_phone = function() {
    var result = jQuery('html').hasClass('is-mobile');
    return result;
  };
  var isResizeEnable = function() {
    if (props && typeof props.resizable === 'boolean') {
      return props.resizable;
    }
    return true;
  };
  var getPositionTop = function() {
    if (props && props.aaPosition) {
      switch (props.aaPosition.vertical) {
        case 'top':
          return 0;
        case 'middle':
          return jQuery(document).height() / 2;
        case 'bottom':
          return jQuery(document).height();
      }
    }
    return jQuery(window).scrollTop() + 10;
  };
  if (dialogObj.length <= 0) {
    return false;
  }
  if (jQuery(dialogObj).length <= 0) {
    return false;
  }
  if (dialogArray[dialogObj] !== undefined && props === undefined) {
    props = dialogArray[dialogObj];
  } else {
    self.initDialog();
  }
}
function aa_Utilities_Format() {
  var self = this;
  self.formatNumber = function(n, decimals, decimal_sep, thousands_sep) {
    var c = isNaN(decimals) ? 2 : Math.abs(decimals), d = decimal_sep || '.',
        t = (typeof thousands_sep === 'undefined') ? ',' : thousands_sep,
        sign = (n < 0) ? '-' : '',
        i = parseInt(n = Math.abs(n).toFixed(c)) + '',
        j = ((j = i.length) > 3) ? j % 3 : 0;
    return sign + (j ? i.substr(0, j) + t : '') +
        i.substr(j).replace(/(\d{3})(?=\d)/g, '$1' + t) +
        (c ? d + Math.abs(n - i).toFixed(c).slice(2) : '');
  };
  self.formatFare = function(number, options) {
    options = (options !== undefined) ? options : {};
    options.currency = (options.currency !== undefined) ?
        options.currency.toUpperCase() :
        null;
    options.locale =
        (options.locale !== undefined) ? options.locale.toLowerCase() : null;
    options.decimals = (options.decimals !== undefined) ?
        ((!isNaN(options.decimals)) ? Math.abs(options.decimals) : null) :
        null;
    options.displayCode =
        (options.displayCode !== undefined) ? options.displayCode : false;
    options.displaySymbol =
        (options.displaySymbol !== undefined) ? options.displaySymbol : true;
    var formatLike = {
      US: {ds: '.', ts: ','},
      BR: {ds: ',', ts: '.'},
      FR: {ds: ',', ts: ' '},
      CH: {ds: '.', ts: '\''}
    };
    var localeLike = {
      US: [
        'ae', 'au', 'ca', 'cn', 'eg', 'gb', 'hk', 'il', 'in', 'jp', 'sk', 'th',
        'tw', 'us'
      ],
      BR: ['at', 'br', 'de', 'dk', 'es', 'gr', 'it', 'nl', 'pt', 'tr', 'vn'],
      FR: ['cz', 'fi', 'fr', 'ru', 'se', 'pl'],
      CH: ['ch']
    };
    var currencies = {
      USD: {code: 'USD', sym: '$', fmt: formatLike.US, dec: 2},
      CAD: {code: 'CAD', sym: '$', fmt: formatLike.US, dec: 2},
      MXN: {code: 'MXN', sym: '$', fmt: formatLike.US, dec: 2},
      GBP: {code: '', sym: '&pound;', fmt: formatLike.US, dec: 2},
      JPY: {code: 'JPY', sym: '&yen;', fmt: formatLike.US, dec: 2},
      COP: {code: 'COP', sym: '$', fmt: formatLike.BR, dec: 2},
      VEF: {code: 'VEF', sym: 'Bs.', fmt: formatLike.BR, dec: 2},
      BRL: {code: 'BRL', sym: 'R$', fmt: formatLike.BR, dec: 2},
      EUR: {code: 'EUR', sym: '&euro;', fmt: formatLike.BR, dec: 2},
      CLP: {code: 'CLP', sym: '$', fmt: formatLike.BR, dec: 0},
      NA: {code: '', sym: '$', fmt: formatLike.US, dec: 2}
    };
    if (options.locale !== null) {
      var localeKey = '';
      for (var key in localeLike) {
        var obj = localeLike[key];
        if (localeKey !== '') {
          break;
        }
        if (!localeLike.hasOwnProperty(key)) {
          continue;
        }
        if (typeof (obj) != 'object' && typeof (obj.length) != 'number') {
          continue;
        }
        for (var z = 0; z < obj.length; z++) {
          if (options.locale === obj[z]) {
            localeKey = key;
            currencies.NA.fmt = formatLike[localeKey];
            break;
          }
        }
      }
    }
    var curr;
    if (options.currency !== null) {
      curr = currencies[options.currency];
    } else {
      if (options.locale !== null) {
        curr = currencies.NA;
      }
    }
    if (curr === undefined) {
      curr = currencies.USD;
    }
    if (options.decimals !== null) {
      curr.dec = options.decimals;
    }
    if (options.displayCode !== true) {
      curr.code = '';
    }
    if (options.displaySymbol !== true) {
      curr.sym = '';
    }
    var result = '%s%n %c';
    result = result.replace(/%s/g, curr.sym);
    result = result.replace(/%c/g, curr.code);
    result = result.replace(
        /%n/g, self.formatNumber(number, curr.dec, curr.fmt.ds, curr.fmt.ts));
    result = result.replace(/^\s+|\s+$/g, '');
    return result;
  };
}