AAcom.modules.browserdetect = function(AAUI) {
  var BrowserDetect = {
    init: function() {
      this.browser =
          this.searchString(this.dataBrowser) || 'An unknown browser';
      this.version = this.searchVersion(navigator.userAgent) ||
          this.searchVersion(navigator.appVersion) || 'an unknown version';
    },
    searchString: function(data) {
      for (var i = 0; i < data.length; i++) {
        var dataString = data[i].string;
        var dataProp = data[i].prop;
        this.versionSearchString = data[i].versionSearch || data[i].identity;
        if (dataString) {
          if (dataString.indexOf(data[i].subString) != -1) {
            return data[i].identity;
          }
        } else {
          if (dataProp) {
            return data[i].identity;
          }
        }
      }
    },
    searchVersion: function(dataString) {
      var index = dataString.indexOf(this.versionSearchString);
      if (index == -1) {
        return;
      }
      return parseFloat(
          dataString.substring(index + this.versionSearchString.length + 1));
    },
    dataBrowser: [
      {string: navigator.userAgent, subString: 'Chrome', identity: 'Chrome'}, {
        string: navigator.vendor,
        subString: 'Apple',
        identity: 'Safari',
        versionSearch: 'Version'
      },
      {string: navigator.userAgent, subString: 'Firefox', identity: 'Firefox'},
      {
        string: navigator.userAgent,
        subString: 'MSIE',
        identity: 'Explorer',
        versionSearch: 'MSIE'
      }
    ]
  };
  BrowserDetect.init();
  AAUI.isUnsupportedBrowser = function() {
    if ((BrowserDetect.browser === 'Firefox' && BrowserDetect.version < 3.6) ||
        (BrowserDetect.browser === 'Safari' && BrowserDetect.version < 5) ||
        (BrowserDetect.browser === 'Chrome' && BrowserDetect.version < 5) ||
        (BrowserDetect.browser === 'Explorer' && BrowserDetect.version < 11)) {
      return true;
    }
    return false;
  };
  AAUI.isIeAndCompatibilityMode = function() {
    if (BrowserDetect.browser === 'Explorer') {
      var agentStr = navigator.userAgent;
      if (((agentStr.indexOf('Trident/6.0') > -1) &&
           (agentStr.indexOf('MSIE 7.0') > -1)) ||
          ((agentStr.indexOf('Trident/5.0') > -1) &&
           (agentStr.indexOf('MSIE 7.0') > -1)) ||
          ((agentStr.indexOf('Trident/4.0') > -1) &&
           (agentStr.indexOf('MSIE 7.0') > -1))) {
        return true;
      }
    }
    return false;
  };
};