AAcom.modules.ajax = function(AAUI) {
  AAUI.ajaxInProgress = false;
  AAUI.ajaxRequest = function(options) {
    var defaults = {
      url: '',
      type: 'GET',
      data: '',
      dataType: 'html',
      async: true,
      cache: false,
      timeout: 30000,
      form: '',
      showBusy: true,
      updateContainer: '',
      busyContainer: undefined,
      busyMessage: '',
      onBeforeSend: function() {},
      onError: undefined,
      onSuccess: function() {},
      onComplete: function() {}
    },
        form = _getFormDetails(options),
        settings = $j.extend({}, defaults, form, options);
    if (!AAUI.ajaxInProgress && settings.url !== '') {
      if (settings.dataType === 'json') {
        settings.contentType = 'application/json';
        if (typeof (settings.data) !== 'string') {
          settings.data = JSON.stringify(settings.data);
        }
      }
      settings = $j.extend(settings, {
        beforeSend: function() {
          AAUI.ajaxInProgress = true;
          if (settings.showBusy) {
            settings.busyContainer =
                settings.busyContainer || settings.updateContainer;
            $j(settings.busyContainer)
                .aaBusy({message: settings.busyMessage})
                .start();
          }
          settings.onBeforeSend();
        },
        success: function(response, statusText, xhr) {
          AAUI.sessionTimeOutDialog.resetTimersToContinue();
          if (!_errorHandler(xhr, statusText, settings)) {
            if (settings.dataType === 'html') {
              $j(settings.updateContainer).empty().html(xhr.responseText);
            }
            settings.onSuccess(response, statusText, xhr);
          }
        },
        error: function(xhr, statusText) {
          AAUI.sessionTimeOutDialog.resetTimersToContinue();
          _errorHandler(xhr, statusText, settings);
        },
        complete: function(xhr, statusText) {
          if (settings.showBusy) {
            $j(settings.busyContainer).aaBusy().stop();
          }
          settings.onComplete(xhr, statusText);
          AAUI.ajaxInProgress = false;
        }
      });
      $j.ajax(settings);
    }
  };
  var _getFormDetails = function(options) {
    var $form = $j(options.form), details;
    if ($form.length > 0) {
      details = {
        url: $form.attr('action'),
        type: $form.attr('method'),
        data: (options.dataType === 'json') ? $form.serializeObject() :
                                              $form.serialize()
      };
    }
    return details;
  };
  var _errorHandler = function(xhr, statusText, settings) {
    if (statusText !== 'success') {
      if (settings.onError !== undefined) {
        settings.onError(xhr, statusText);
      } else {
        var $htmlResponse = $j(xhr.responseText);
        if (statusText === 'timeout' || xhr.responseText === 'invalidState' ||
            $htmlResponse.find('.js-invalidState').length > 0) {
          top.location.href = '/invalidState.do';
          return true;
        } else {
          if (statusText === 'error' || xhr.responseText === 'systemError' ||
              $htmlResponse.find('.js-systemError').length > 0) {
            top.location.href = '/systemError.do';
            return true;
          }
        }
      }
    }
    return false;
  };
};
if (!$j.isFunction($j.fn.serializeObject)) {
  $j.fn.serializeObject = function() {
    var o = {};
    var a = this.serializeArray();
    $j.each(a, function() {
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
}