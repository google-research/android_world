AAcom.modules.utilities = function(AAUI) {
  AAUI.onClick = function(selector, callback) {
    $j(document).on('click', selector, function(e) {
      this.callback = callback;
      var result = this.callback(e) || false;
      return result;
    });
  };
  AAUI.onChange = function(selector, callback) {
    $j(document).on('change', selector, callback);
  };
  AAUI.onMouseEnter = function(selector, callback) {
    $j(document).on('mouseenter', selector, callback);
  };
  AAUI.onMouseLeave = function(selector, callback) {
    $j(document).on('mouseleave', selector, callback);
  };
  AAUI.onFocus = function(selector, callback) {
    $j(document).on('focus', selector, callback);
  };
  AAUI.onBlur = function(selector, callback) {
    $j(document).on('blur', selector, callback);
  };
  AAUI.onSubmit = function(selector, callback) {
    $j(document).on('submit', selector, callback);
  };
  AAUI.onKeyup = function(selector, callback) {
    $j(document).on('keyup', selector, callback);
  };
  AAUI.onKeyPress = function(selector, callback) {
    $j(document).on('keypress', selector, callback);
  };
  AAUI.onKeyChange = function(selector, callback) {
    AAUI.onChange(selector, callback);
    AAUI.onKeyup(selector, function(e) {
      var tabKey = 9, shiftKey = 16;
      if (!(e.keyCode == tabKey || e.keyCode == shiftKey)) {
        $j(this).trigger('change');
      }
    });
  };
  AAUI.onInput = function(selector, callback) {
    $j(document).on('input', selector, callback);
    if ($j('html').hasClass('lt-ie10')) {
      $j(document).on('cut', selector, callback);
      $j(document).on('keyup', selector, function(e) {
        var keyCode = e.keyCode || e.which;
        if (keyCode == 8 || keyCode == 46) {
          this.callback = callback;
          this.callback(e);
        }
      });
    }
  };
  AAUI.off = function(event, selector, callback) {
    $j(document).off(event, selector, callback);
  };
  var genericPopupUtility = {
    popup: function(
        windowUrl, windowName, windowSize, windowWidth, windowHeight) {
      var windowLeft = 0, windowTop = 0, windowFeatures = '',
          windowObject = null;
      windowUrl = windowUrl || '';
      windowName = windowName || '';
      windowSize = windowSize || 'MEDIUM';
      windowWidth = windowWidth || this.defaultWidth;
      windowHeight = windowHeight || this.defaultHeight;
      windowSize = windowSize.toUpperCase();
      windowWidth = parseInt(windowWidth);
      windowHeight = parseInt(windowHeight);
      switch (windowSize) {
        case 'SMALL':
          windowWidth = 300;
          windowHeight = 300;
          break;
        case 'MEDIUM':
          windowWidth = this.defaultWidth;
          windowHeight = this.defaultHeight;
          break;
        case 'LARGE':
          windowWidth = 850;
          windowHeight = 500;
          break;
        case 'SCREEN':
          windowWidth = $j(window).width() - 50;
          windowHeight = $j(window).height() - 50;
          break;
      }
      windowLeft =
          Math.floor(screen.availWidth / 2) - Math.floor(windowWidth / 2);
      windowTop =
          Math.floor(screen.availHeight / 2) - Math.floor(windowHeight / 2);
      if (windowSize === 'SCREEN') {
        windowFeatures =
            'location=1, status=1, scrollbars=1, menubar=1, toolbar=1, resizable=1';
      } else {
        windowFeatures =
            'location=0, status=0, scrollbars=1, menubar=0, toolbar=0, resizable=1';
      }
      windowFeatures = windowFeatures + ',width=' + windowWidth +
          ',height=' + windowHeight + ',top=' + windowTop +
          ',left=' + windowLeft;
      if ($j('html').hasClass('lt-ie10')) {
        windowName = 'popupWindow';
      }
      windowObject = window.open(windowUrl, windowName, windowFeatures);
      if (windowObject !== null) {
        windowObject.focus();
        return windowObject;
      }
    },
    defaultWidth: 675,
    defaultHeight: 500
  };
  AAUI.genericPopup = function(element) {
    element.on('click', function() {
      var size = '';
      if (!$j(this).attr('data-size')) {
        switch (true) {
          case $j(this).hasClass('aa-pop-win-sm'):
            size = 'SMALL';
            break;
          case $j(this).hasClass('aa-pop-win-med'):
            size = 'MEDIUM';
            break;
          case $j(this).hasClass('aa-pop-win-lrg'):
            size = 'LARGE';
            break;
          case $j(this).hasClass('aa-pop-win-new'):
            size = 'SCREEN';
            break;
          default:
            size = 'MEDIUM';
        }
      } else {
        size = $j(this).attr('data-size');
      }
      genericPopupUtility.popup(
          $j(this).attr('href'), $j(this).attr('title'), size,
          $j(this).attr('data-width'), $j(this).attr('data-height'));
      return false;
    });
  };
  AAUI.genericManualPopup = function(windowUrl, windowName, windowSize) {
    genericPopupUtility.popup(windowUrl, windowName, windowSize, 0, 0);
  };
  AAUI.getQueryStringParameterByName = function(name) {
    name = name.replace(/[\[]/, '\\[').replace(/[\]]/, '\\]');
    var regex = new RegExp('[\\?&]' + name + '=([^&#]*)');
    var results = regex.exec(location.search);
    return results === null ?
        '' :
        decodeURIComponent(results[1].replace(/\+/g, ' '));
  };
  AAUI.populateFormFromJSON = function(data) {
    $j.each(data, function(name, val) {
      var $el = $j('[name="' + name + '"]'), type = $el.attr('type');
      switch (type) {
        case 'checkbox':
          $el.removeAttr('checked');
          $el.filter('[value="' + val + '"]').attr('checked', 'checked');
          break;
        case 'radio':
          $el.filter('[value="' + val + '"]').attr('checked', 'checked');
          break;
        default:
          $el.val(val).trigger('change');
      }
    });
  };
  AAUI.populateFormErrorsFromJSON = function(formID, data) {
    $j.each(data, function(name, message) {
      var globalErrorStartsWith = 'ERRCODE';
      if (name.substring(0, globalErrorStartsWith.length) ===
          globalErrorStartsWith) {
        $errorContainer = $j(formID + 'Errors');
        $errorContainer.append(message)
            .addClass('message-inline-error')
            .removeClass('is-hidden');
      } else {
        var $el = $j('[name="' + name + '"]:visible'),
            errorsID = name + 'Errors',
            errorsID = errorsID.replace(/[\[]/, '\\[')
                           .replace(/[\]]/, '\\]')
                           .replace(/\./g, '\\.'),
            proxyLabelID = $el.attr('data-proxy-label'),
            $errorContainer = $j('#' + errorsID);
        $j('label[for=\'' + $el.attr('id') + '\']').addClass('is-error');
        $j('#' + proxyLabelID).addClass('is-error');
        $errorContainer.append(message);
        if ($errorContainer.data('composite_error')) {
          $errorContainer.parent()
              .find('.js-compositeFieldError')
              .append(message);
        }
        AAUI.errorSummary.showLink(name);
      }
    });
  };
  AAUI.clearFormErrors = function(container) {
    var $container = $j(container);
    $container.find('.is-error.-message').empty();
    $container.find('.is-error')
        .removeClass('is-error')
        .removeClass('-message');
    $container.find('.message-inline-error')
        .removeClass('message-inline-error');
    var errorMessageContainers =
        $container.find('[id$="Errors"],[id$=".errors"]');
    $j.each(errorMessageContainers, function() {
      $j(this).empty().removeClass('message-inline-error');
      $j(this).parent().find('.js-compositeFieldError').empty();
    });
  };
  AAUI.clearInputValueAndErrors = function(whichInputID) {
    var thisInput = $j(whichInputID),
        thisInputErrors = $j(whichInputID + 'Errors');
    thisInput.val('').removeClass('is-error');
    thisInputErrors.html('').removeClass('is-error').removeClass('-message');
    $j('label[for=\'' + thisInput.attr('id') + '\']').removeClass('is-error');
  };
  AAUI.resetFormFields = function(container) {
    $j(container).find(':input').each(function() {
      var $el = $j(this), type = $el.attr('type');
      switch (type) {
        case 'checkbox':
          $el.removeAttr('checked').trigger('change');
          break;
        case 'radio':
          if (!$el.hasClass('js-pillbox')) {
            $el.removeAttr('checked');
          }
          break;
        case 'text':
          $el.val('');
          break;
        default:
          $el.prop('selectedIndex', 0).trigger('change');
      }
    });
  };
  AAUI.setDialogTitle = function(whichDialogID, titleString) {
    $j(whichDialogID).dialog('option', 'title', titleString);
  };
  AAUI.ignoreChangesDialog = function() {
    var self = {};
    self.init = function() {
      var buttons = [
        {
          name: AAUI.getProperty('btn.yes'),
          cssClass: 'btn',
          callback: self.reload,
          closeDialog: false
        },
        {name: AAUI.getProperty('btn.no'), cssClass: 'btn'}
      ];
      AAUI.util.aaDialog(
          'ignoreChanges',
          {width: 'small', buttons: buttons, toggleScroll: true});
      AAUI.onClick('.js-ignoreChanges', self.open);
    };
    self.open = function() {
      self.href = $j(this).attr('data-href');
      AAUI.util.aaDialog('ignoreChanges').openDialog();
    };
    self.reload = function() {
      window.location.href = self.href;
      return false;
    };
    return self;
  }();
  AAUI.tier1 = function() {
    var self = {};
    self.setFocus = function(selector) {
      selector = selector || '.message-error,.message-warning,.message-info';
      $tier1Heading = $j(selector).filter(':visible:first').find('.header');
      AAUI.setFocusOn($tier1Heading);
    };
    return self;
  }();
  AAUI.errorSummary = function() {
    var self = {}, _errorSummary = '.js-errorSummary';
    self.init = function(pageLoad) {
      AAUI.onClick(_errorSummary + ' a', self.clickLink);
    };
    self.setFocus = function() {
      AAUI.tier1.setFocus('.message-error');
    };
    self.clickLink = function() {
      var target = $j(this)
                       .attr('href')
                       .replace(/\./g, '\\.')
                       .replace(/[\[]/, '\\[')
                       .replace(/[\]]/, '\\]');
      AAUI.setFocusOn(target);
    };
    self.hideLinks = function(container) {
      $j(container).find(_errorSummary + ' li').addClass('is-hidden');
    };
    self.showLink = function(name) {
      $j(_errorSummary + ' a[id="' + name + '.link"]')
          .parents('li')
          .removeClass('is-hidden');
    };
    return self;
  }();
  AAUI.setFocusOn = function(target) {
    var $target = $j(target).filter(':first:visible');
    if ($target.length > 0) {
      if ($target.filter(':input,a').length === 0 &&
          $target.attr('tabindex') === undefined) {
        $target.attr('tabindex', '-1');
      }
      if ($target.parents('.ui-dialog:first').length === 0) {
        var topPosition = $target.parent().offset().top - 50;
        $j('html,body').animate({scrollTop: topPosition});
      }
      $target.focus();
    }
  };
  AAUI.sessionTimeOutDialog = function() {
    var self = {}, renewTimer, aaUtilities, $sessionTimeoutDialog, $title,
        $body, $continueButton, $homeButton, $isDisplayVirtualPNRModal,
        $isFinalDisplayModal, $bookingPathStateId,
        _dialogID = '#sessionTimeOutDialog';
    self.init = function() {
      $j(document).ready(function() {
        if ($j(_dialogID).filter('.js-spring').length > 0) {
          aaUtilities = new aa_Utilities();
          var buttons = [
            {
              name: AAUI.getProperty('session.warning.button'),
              cssClass: 'btn no-margin',
              callback: self.continueSession,
              closeDialog: false
            },
            {
              name: AAUI.getProperty('session.expired.button'),
              cssClass: 'btn no-margin is-hidden',
              callback: self.home,
              closeDialog: false
            }
          ];
          aaUtilities.aaDialog('sessionTimeOut', {
            width: 'small',
            buttons: buttons,
            toggleScroll: true,
            showClose: false,
            closeOnEscape: false,
            zIndex: 99999
          });
          self.sessionDialogElements();
          self.startSessionTimer();
        }
      });
    };
    self.sessionDialogElements = function() {
      $sessionTimeoutDialog = jQuery(_dialogID).parents('.ui-dialog:first'),
      $title = $sessionTimeoutDialog.find('.ui-dialog-title'),
      $body = $sessionTimeoutDialog.find('.js-dialogBody'),
      $continueButton = $sessionTimeoutDialog.find(_dialogID + 'Button0'),
      $homeButton = $sessionTimeoutDialog.find(_dialogID + 'Button1');
      $isDisplayVirtualPNRModal = AAUI.getProperty('isDisplayVirtualPNRModal');
      $isFinalDisplayModal = AAUI.getProperty('isFinalDisplay');
      $bookingPathStateId = AAUI.getProperty('bookingPathStateId');
    };
    self.open = function() {
      aaUtilities.aaDialog('sessionTimeOut').openDialog();
      self.startSessionRenewTimer();
    };
    self.startSessionTimer = function() {
      var sessionTimeoutBuffer = 5000;
      var sessionExpiresWarningInterval =
          AAUI.getProperty('sessionExpiresWarningInterval');
      var sessionMaxInactiveTime = AAUI.getProperty('sessionTimeOut') * 1000;
      var sessionWarningCountDown = 0;
      if (self.finalDisplay()) {
        renewTimer = setTimeout(function() {
          self.sessionExpiredDialog();
        }, sessionMaxInactiveTime - sessionTimeoutBuffer);
        sessionTimer = null;
      } else {
        var sessionWarningCountDown = sessionMaxInactiveTime -
            sessionExpiresWarningInterval - sessionTimeoutBuffer;
        sessionTimer = setTimeout(function() {
          self.open();
        }, sessionWarningCountDown);
      }
    };
    self.startSessionRenewTimer = function() {
      var sessionExpiresWarningInterval =
          AAUI.getProperty('sessionExpiresWarningInterval');
      renewTimer = setTimeout(function() {
        self.sessionExpiredDialog();
      }, sessionExpiresWarningInterval);
    };
    self.sessionExpiredDialog = function() {
      $title.html(AAUI.getProperty('session.expired.title'));
      $body.html(AAUI.getProperty('session.expired.message'));
      $continueButton.addClass('is-hidden');
      $homeButton.removeClass('is-hidden');
      aaUtilities.aaDialog('sessionTimeOut').closeDialog();
      aaUtilities.aaDialog('sessionTimeOut').openDialog();
      if (self.virtualPNRExists()) {
        deleteVirtualPNR();
      }
    };
    self.continueSession = function() {
      self.stopTimers();
      var params = self.createVirtualPnrParams();
      AAUI.ajaxRequest({
        url: '/shared/session/renew/' + params,
        type: 'POST',
        dataType: 'json',
        busyContainer: $j('#sessionTimeOut').parent(),
        busyMessage: '',
        timeout: 50000,
        onSuccess: function(jsonResponse) {
          if (self.virtualPNRExists()) {
            self.handleUpdateVirtualPnrResponse(jsonResponse);
          } else {
            self.resetTimersToContinue();
          }
        },
        onError: function(xhr, statusText) {
          self.stopTimers();
          self.open();
          self.sessionExpiredDialog();
        }
      });
      aaUtilities.aaDialog('sessionTimeOut').closeDialog();
      return false;
    };
    self.createVirtualPnrParams = function() {
      if (self.virtualPNRExists()) {
        return '?virtualPnr=true&bookingPathStateId=' + $bookingPathStateId;
      }
      return '';
    };
    self.stopTimers = function() {
      clearTimeout(renewTimer);
      renewTimer = null;
      clearTimeout(sessionTimer);
      sessionTimer = null;
    };
    self.resetTimersToContinue = function() {
      self.stopTimers();
      self.startSessionTimer();
    };
    self.virtualPNRExists = function() {
      var returnValue = false;
      if ($isDisplayVirtualPNRModal == 'true' ||
          $isDisplayVirtualPNRModal == true) {
        returnValue = true;
      }
      return returnValue;
    };
    self.finalDisplay = function() {
      var returnValue = false;
      if ($isFinalDisplayModal == 'true' || $isFinalDisplayModal == true) {
        returnValue = true;
      }
      return returnValue;
    };
    self.handleUpdateVirtualPnrResponse = function(response) {
      $isFinalDisplayModal = response.finalVirtualPNRModal;
      self.resetTimersToContinue();
    };
    self.home = function() {
      AAUI.ajaxRequest({
        url: '/shared/session/expired/',
        type: 'POST',
        dataType: 'text',
        busyContainer: $j('#sessionTimeOut').parent(),
        busyMessage: '',
        timeout: 50000,
        onSuccess: function(jsonResponse) {
          window.location.href = jsonResponse;
        },
        onError: function() {
          window.location.href = '/homePage.do';
        }
      });
    };
    return self;
  }();
  AAUI.characterCount = function() {
    self.init = function() {
      AAUI.onInput('.js-commentsArea', self.calculate);
      AAUI.onInput(
          '.js-assistanceTypeCommentsArea', self.assistanceTypeCalculate);
    };
    self.calculate = function() {
      var $textField = $j(this), maxLength = $textField.attr('maxlength'),
          usedLength = $textField.val().length;
      $j('.js-characterCounter').html(maxLength - usedLength);
    };
    self.assistanceTypeCalculate = function() {
      var $textField = $j(this), maxLength = $textField.attr('maxlength'),
          usedLength = $textField.val().length;
      $j('.js-assistanceTypeCharacterCounter').html(maxLength - usedLength);
    };
    return self;
  }();
  AAUI.toPascalCase = function(content) {
    var formattedContent = AAUI.pascalCaseContent(content);
    formattedContent = formattedContent.replace('-A-', '-a-');
    formattedContent = formattedContent.replace('(u.s.)', '(U.S.)');
    formattedContent = formattedContent.replace('(british)', '(British)');
    return formattedContent.trim();
  };
  AAUI.pascalCaseContent = function(content) {
    var splitter = ' ';
    var formattedWord = '';
    var formattedContent = '';
    var wordArray = content.split(splitter);
    var lastWordIndex = wordArray.length - 1;
    for (i = 0; i < wordArray.length; i++) {
      formattedWord = AAUI.pascalCaseWord(wordArray[i]);
      formattedWord = AAUI.pascalCaseContentWithSplitter('-', formattedWord);
      formattedWord = AAUI.pascalCaseContentWithSplitter('/', formattedWord);
      formattedContent += formattedWord;
      if (i != lastWordIndex) {
        formattedContent += splitter;
      }
    }
    return formattedContent.trim();
  };
  AAUI.pascalCaseContentWithSplitter = function(splitter, content) {
    if (content.indexOf(splitter) == -1) {
      return content;
    }
    var formattedWord;
    var formattedContent = '';
    var wordArray = content.split(splitter);
    var lastWordIndex = wordArray.length - 1;
    for (x = 0; x < wordArray.length; x++) {
      formattedWord = AAUI.pascalCaseWord(wordArray[x]);
      formattedContent += formattedWord;
      if (x != lastWordIndex) {
        formattedContent += splitter;
      }
    }
    return formattedContent.trim();
  };
  AAUI.pascalCaseWord = function(word) {
    return word.charAt(0).toUpperCase() + word.substring(1).toLowerCase();
  };
  AAUI.genericPopup($j('.aa-pop-win-med'));
  AAUI.genericPopup($j('.aa-pop-win-lrg'));
  AAUI.errorSummary.init();
  AAUI.sessionTimeOutDialog.init();
};