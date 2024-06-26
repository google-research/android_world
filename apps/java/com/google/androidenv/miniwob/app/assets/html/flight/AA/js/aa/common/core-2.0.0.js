function deleteVirtualPNR() {
  var bps = $j('input[name=bookingPathStateId]').val();
  if ((bps != null && bps != '') || bps == 'undefined') {
    var jsonData = '{ "bps": "' + bps + '" }';
    jQuery.ajax({
      type: 'GET',
      url: '/home/ajax/cancelVPNR',
      data: {bps: bps},
      contentType: 'application/json; charset=UTF-8',
      async: true,
      cache: false,
      timeout: 60000,
      dataType: 'json'
    });
  }
}
var initPageSlide = function() {
  var _is_WindowOrientationChanged = false;
  var _is_PageSlideOpen = false;
  if (jQuery('.pageslide-button').hasClass('ui-state-initialized')) {
    return;
  }
  jQuery(window).bind('orientationchange', function() {
    _is_WindowOrientationChanged = true;
    if (_is_PageSlideOpen) {
      closePageSlide();
    }
  });
  jQuery(window).resize(function() {
    if (typeof ($device) !== 'undefined' && $device.viewport() != 'phone' &&
        _is_PageSlideOpen) {
      closePageSlide();
    }
  });
  jQuery('html').on('click', function(event) {
    if (_is_PageSlideOpen &&
        !jQuery(event.target).closest('#navigation').length) {
      closePageSlide();
    }
  });
  jQuery('.pageslide-button').click(function(event) {
    var pageSlideId = jQuery(this).attr('href');
    var pageSlidePos = jQuery(this).attr('data-position');
    if (!_is_PageSlideOpen) {
      openPageSlide(pageSlideId, pageSlidePos, this);
    } else {
      closePageSlide();
    }
    return false;
  });
  var openPageSlide = function(pageSlideId, pageSlidePos, pageSlideBtn) {
    var _pageSlideWidth = 260;
    var _animationTime = 300;
    if (pageSlidePos == 'right') {
      jQuery('body')
          .css({left: ''})
          .animate({right: _pageSlideWidth}, _animationTime);
      jQuery(pageSlideId).css({right: -_pageSlideWidth});
    } else {
      jQuery('body')
          .css({right: ''})
          .animate({left: _pageSlideWidth}, _animationTime);
      jQuery(pageSlideId).css({left: -_pageSlideWidth});
    }
    jQuery('body').css('overflow-x', 'hidden');
    jQuery(pageSlideId).addClass('pageslide');
    jQuery('.pageslide-row').css({position: 'inherit'});
    (pageSlideBtn !== undefined) ?
        jQuery(pageSlideBtn).addClass('icon-on') :
        jQuery('.pageslide-button').addClass('icon-on');
    _is_PageSlideOpen = true;
  };
  var closePageSlide = function() {
    var _body = jQuery('body');
    if (_body.css('left') > 0) {
      var _animateElement = {left: 0};
    } else {
      var _animateElement = {right: 0};
    }
    jQuery('body').animate(_animateElement, 300, function() {
      jQuery(this).find('.pageslide-row').css({position: ''});
      jQuery(this).find('.pageslide').removeAttr('style');
      jQuery(this).find('.pageslide').removeClass('pageslide');
      jQuery('body').css('overflow-x', '');
    });
    jQuery('.pageslide-button').removeClass('icon-on');
    _is_PageSlideOpen = false;
  };
  jQuery('.pageslide-button').addClass('ui-state-initialized');
  return;
};
var initMastheadNav = function() {
  var expanders = jQuery('[data-behavior=toggle-nav]'),
      navigation = jQuery('#navigation'), close = jQuery('#close'),
      commonLinks = jQuery('#nav-common-links'),
      subNavLinks = jQuery('.sub-nav-links'), animationTime = 300;
  if (navigation.hasClass('ui-state-initialized')) {
    return;
  }
  subNavLinks.append(commonLinks.html());
  expanders.on('click', function(ev) {
    ev.preventDefault();
    var expander = jQuery(this), container = expander.parent('li');
    var href = (expander.attr('href') !== undefined) ?
        expander.attr('href') :
        expander.attr('data-toggle-href');
    var target = jQuery(href);
    if (navigation.hasClass('open')) {
      if (container.hasClass('open')) {
        initAnimation(target, expander, container);
      } else {
        expanders.each(function() {
          jQuery(this).removeClass('open');
          jQuery(this).parent('li').removeClass('open');
          jQuery(this).parent('li').find('.sub-nav-links').hide();
          jQuery(this)
              .find('i')
              .removeClass('icon-collapse')
              .addClass('icon-expand');
        });
        expander.addClass('open');
        container.addClass('open');
        target.show();
        expander.find('i').removeClass('icon-expand').addClass('icon-collapse');
      }
    } else {
      initAnimation(target, expander, container);
    }
  });
  close.on('click', function(ev) {
    ev.preventDefault();
    if (navigation.hasClass('open')) {
      expanders.each(function() {
        var expander = jQuery(this);
        if (expander.hasClass('open')) {
          var container = expander.parent('li');
          var target = container.find('.sub-nav-links');
          initAnimation(target, expander, container);
        }
      });
    }
  });
  var initAnimation = function(target, expander, container) {
    target.stop().animate({height: 'toggle'}, {
      duration: 300,
      start: function() {
        close.toggle();
        expander.toggleClass('open');
        container.toggleClass('open');
        navigation.toggleClass('open');
        expander.find('i')
            .toggleClass('icon-expand')
            .toggleClass('icon-collapse');
      },
      complete: function() {
        jQuery(this).css('height', '');
      }
    });
  };
  navigation.addClass('ui-state-initialized');
};
if (jQuery.aaCookie.get('hideMobileAppMarketingMsg')) {
  jQuery('#mobileApplicationMsg').hide();
}
jQuery(document).ready(function() {
  initMastheadNav();
  var regional, placeholderTest = document.createElement('input');
  jQuery.countryLanguageSelector();
  jQuery('#mobileApplicationMsg .close').click(function(e) {
    e.preventDefault();
    jQuery.aaCookie.set('hideMobileAppMarketingMsg', 'true');
    jQuery('#mobileApplicationMsg').hide();
  });
  if (!('placeholder' in placeholderTest)) {
    jQuery('#aa-search-field')
        .aaTextBoxMessage(
            AAcom.prototype.getProperty('label.siteSearch.textboxmessage'));
  }
  initPageSlide();
});