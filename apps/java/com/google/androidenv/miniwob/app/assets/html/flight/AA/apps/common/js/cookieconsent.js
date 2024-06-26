var cookieconsentModule = (function($j) {
  var jQueryVersionArray = $j.fn.jquery.split('.');
  var loaded = false;
  var jQueryUILoaded = false;
  var aaUtilLoaded = false;
  var modalLocale = '';
  var hostNameForConsentCookieServlet = 'www.aa.com';
  var DEBUG = false;
  processConsent = function() {
    debugLog('processConsent..');
    debugLog('$j.fn.jquery: ' + $j.fn.jquery);
    debugLog('$j.ui.version: ' + $j.ui.version);
    makeCorsRequest('GET');
  };
  setConsent = function(value) {
    makeCorsRequest('PUT', value ? '1' : '0');
  };
  getDomainUrl = function() {
    var domainUrl;
    try {
      var cProto =
          ('https:' == document.location.protocol ? 'https://' : 'http://');
      if (location.port != null && location.port.length > 0 &&
          window.location.hostname.toLowerCase().indexOf(
              'local.aadevelop.com') > -1) {
        domainUrl = cProto + window.location.hostname + ':' + location.port;
      } else {
        domainUrl = cProto + hostNameForConsentCookieServlet;
      }
      debugLog('domainUrl: ' + domainUrl);
    } catch (err) {
      debugLog(err);
    }
    return domainUrl;
  };
  getConsentUrl = function() {
    var consentUrl = getDomainUrl() + '/shared/cookieConsent';
    if (modalLocale.length > 0) {
      consentUrl = consentUrl + '?locale=' + modalLocale;
    }
    debugLog(modalLocale);
    debugLog('consentUrl: ' + consentUrl);
    return consentUrl;
  };
  makeCorsRequest = function(method, value) {
    debugLog('value: ' + value);
    try {
      $j.ajax({
        type: method,
        cache: false,
        url: getConsentUrl(),
        contentType: 'text/plain',
        xhrFields: {withCredentials: true},
        crossDomain: true,
        beforeSend: function(xhr) {
          xhr.withCredentials = true;
          debugLog('beforeSend - value: ' + value);
          xhr.setRequestHeader('consentcookieheader', value);
          xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
        },
        success: function(xhr) {
          if (method === 'GET') {
            processJSON(xhr);
          }
        },
        error: function() {
          debugLog('There is an error');
          hideModal();
        }
      });
    } catch (err) {
      debugLog(err);
      hideModal();
    }
  };
  processJSON = function(response) {
    var jsonResponse;
    if ($j.isFunction($j.parseJSON)) {
      jsonResponse = response;
    } else {
      if ($j.isFunction(JSON.parse)) {
        jsonResponse = JSON.parse(response);
      }
    }
    debugLog('jsonResponse.displayFlag: ' + jsonResponse.displayFlag);
    if (jsonResponse.displayFlag === '1') {
      $j('body').append(jsonResponse.htmlText);
      bindEvents();
      showModal();
    } else {
      hideModal();
    }
  };
  showModal = function() {
    aaUtil.aaDialog('cookieConsent').openDialog();
    $j('#cookieConsentDialog')
        .parent()
        .find('.ui-dialog-titlebar')
        .css('marginBottom', 15 + 'px');
  };
  hideModal = function() {
    if (typeof aaUtil !== 'undefined') {
      aaUtil.aaDialog('cookieConsent').closeDialog();
    }
  };
  checkPrerequisiteAndStartProcess = function() {
    if (typeof jQuery.ui === 'undefined' && !jQueryUILoaded) {
      getjQueryUI();
    } else {
      jQueryUILoaded = true;
      getAAUtils();
    }
  };
  getjQueryUI = function() {
    var jQueryUILocation;
    if (jQueryVersionArray.length > 2 && jQueryVersionArray[0] === '1' &&
        jQueryVersionArray[1] > 4) {
      jQueryUILocation = '/js/libs/jquery/ui/1.10/jquery-ui.min.js';
    } else {
      if (jQueryVersionArray.length > 2 && jQueryVersionArray[0] === '1' &&
          jQueryVersionArray[1] === '4') {
        jQueryUILocation =
            '/apps/common/js/jquery/ui/1.8/jquery-ui-1.8.2.custom.min.js';
      } else {
        jQueryUILocation =
            '/apps/common/js/jquery/ui/jquery-ui-1.7.2.custom.min.js';
      }
    }
    var jQueryUIUrl = getDomainUrl() + jQueryUILocation;
    loadScript(jQueryUIUrl, function() {
      debugLog('got jQueryUI at: ' + jQueryUIUrl);
      jQueryUILoaded = true;
      getAAUtils();
    });
  };
  getAAUtils = function() {
    var aaUtilitiesLocation;
    if (typeof aa_Utilities === 'undefined' && !aaUtilLoaded) {
      if (jQueryVersionArray.length > 2 && jQueryVersionArray[0] === '1' &&
          jQueryVersionArray[1] > 4) {
        aaUtilitiesLocation =
            '/apps/common/js/jquery/aacom/utilities/aaUtilities-2.1.js';
      } else {
        aaUtilitiesLocation =
            '/apps/common/js/jquery/aacom/utilities/aaUtilities.js';
      }
      var aaUtilitiesUrl = getDomainUrl() + aaUtilitiesLocation;
      debugLog('aaUtilitiesUrl: ' + aaUtilitiesUrl);
      loadScript(aaUtilitiesUrl, function() {
        aaUtilLoaded = true;
        debugLog('got aa_Utilities at: ' + aaUtilitiesUrl);
        processConsent();
      });
    } else {
      aaUtilLoaded = true;
      processConsent();
    }
  };
  loadScript = function(url, callback) {
    $j.ajax({url: url, dataType: 'script', success: callback, async: true});
  };
  bindEvents = function() {
    aaUtil = new aa_Utilities();
    var buttonText = 'I accept';
    if (typeof acceptCookieConsentText !== 'undefined') {
      buttonText = acceptCookieConsentText;
    }
    var btnArray = new Array();
    btnArray[0] = {
      name: buttonText,
      id: 'cookieConsentAccept',
      cssClass: 'btn',
      closeDialog: true,
      callback: handleCookieConsentAccept
    };
    aaUtil.aaDialog('cookieConsent', {
      width: 575,
      height: 'auto',
      buttons: btnArray,
      toggleScroll: false,
      showClose: false,
      closeOnEscape: false
    });
    try {
      if ($j.isFunction($j('body').delegate)) {
        $j('body').delegate(
            '#cookieConsentPolicyLink', 'click', cookiePolicyClickHandler);
      } else {
        $j('#cookieConsentPolicyLink').live('click', cookiePolicyClickHandler);
      }
    } catch (err) {
      hideModal();
    }
  };
  cookiePolicyClickHandler = function() {
    $j('#cookieConsentPolicy').toggleClass('is-hidden');
  };
  handleCookieConsentAccept = function() {
    setConsent(true);
    hideModal();
  };
  setModalLocale = function(locale) {
    modalLocale = locale;
    debugLog('modal locale: ' + locale);
  };
  setConsentServletHost = function(hostName) {
    try {
      if ((typeof hostName !== 'undefined' && hostName.length > 0) &&
          window.location.hostname.toLowerCase().indexOf('www.aa.com') < 0) {
        hostNameForConsentCookieServlet = hostName;
      }
    } catch (err) {
    }
    debugLog('hostNameForConsentCookieServlet: ' + hostName);
  };
  debugLog = function(message) {
    if (DEBUG) {
      console.log(message);
    }
  };
  return {
    start: function() {
      if (loaded === false) {
        loaded = true;
        try {
          checkPrerequisiteAndStartProcess();
        } catch (err) {
          debugLog(err);
          hideModal();
        }
      }
    },
    setLocale: setModalLocale,
    setServiceHost: setConsentServletHost
  };
})(jQuery);
jQuery(document).ready(function() {
  cookieconsentModule.start();
});