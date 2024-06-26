AAcom.modules.aaDatePicker = function(AAUI) {
  var _isIE = function() {
    var ua = window.navigator.userAgent;
    var msie = ua.indexOf('MSIE ');
    return msie > 0 || !!navigator.userAgent.match(/Trident.*rv\:11\./);
  };
  var _setDatePickerDefaults = function() {
    var userLocale = AAUI.getProperty('user.locale');
    if (typeof $j.datepicker.regional[userLocale] == 'undefined') {
      if (typeof $j.datepicker.regional[userLocale.substring(0, 2)] ==
          'undefined') {
        regional = $j.datepicker.regional[''];
      } else {
        regional = $j.datepicker.regional[userLocale.substring(0, 2)];
      }
    } else {
      regional = $j.datepicker.regional[userLocale];
    }
    $j.datepicker.setDefaults(regional);
    var is_responsive =
        (typeof ($device) !== 'undefined' && $device.responsive);
    var is_mobile =
        (is_responsive && typeof ($device) !== 'undefined' && $device.mobile);
    var datePickerMonths =
        (typeof ($device) !== 'undefined' && $device.viewport() == 'phone') ?
        1 :
        2;
    $j.datepicker.setDefaults({
      fixFocusIE: false,
      disabled: false,
      numberOfMonths: datePickerMonths,
      showButtonPanel: true,
      minDate: 0,
      maxDate: +331,
      hideIfNoPrevNext: true,
      showAnim: 'fadeIn',
      buttonText: '',
      showOn: 'both',
      beforeShow: function(input, inst) {
        var result = _isIE() ? !this.fixFocusIE : true;
        this.fixFocusIE = false;
        return result;
      },
      onClose: function(dateText, inst) {
        this.fixFocusIE = true;
      }
    });
    if (is_responsive) {
      $j(window).resize(function() {
        if ($j('.ui-datepicker').is(':visible') && $device.desktop) {
          $j('.aaDatePicker').datepicker('hide').blur();
        }
        var datePickerMonths = (typeof ($device) !== 'undefined' &&
                                $device.viewport() == 'phone') ?
            1 :
            2;
        $j.datepicker.setDefaults({numberOfMonths: datePickerMonths});
      });
    }
  };
  AAUI.initDatePicker = function(id, options) {
    $j(id).datepicker(options);
    $j('button.ui-datepicker-trigger')
        .append(
            '<span class=\'hidden-accessible\'>' +
            AAUI.getProperty('calendar.hiddenText') + '</span>');
    var weeksList =
        $j('#ui-datepicker-div').find('.ui-datepicker-calendar>thead>tr>th');
    var message = '';
    $j(id).keydown(function(event) {
      if (event.keyCode == 8 || (event.keyCode >= 48 && event.keyCode <= 57) ||
          event.keyCode == 191) {
        $j(id).datepicker('hide');
      }
      if (weeksList.length === 0) {
        weeksList = $j('#ui-datepicker-div')
                        .find('.ui-datepicker-calendar>thead>tr>th');
      }
      var message = $j(weeksList[$j('.ui-state-hover').closest('td').index()])
                        .find('span')
                        .attr('title');
      if (message !== undefined) {
        message += ', ' + $j('.ui-datepicker-month').html() + ' ' +
            $j('.ui-state-hover').html() + ' ' +
            $j('.ui-datepicker-year').html() + '.';
      } else {
        message = '';
      }
      $j('#ariaLiveReaderContainer').attr('aria-live', 'polite').text(message);
    });
    AAUI.onBlur(id, function(e) {
      try {
        $j.datepicker.parseDate(
            $j.datepicker._defaults.dateFormat, $j(this).val());
      } catch (error) {
        $j('#ariaLiveReaderContainer').text('');
      }
    });
  };
  _setDatePickerDefaults();
  AAUI.isValidDatepickerDate = function(selector) {
    try {
      var selectedDate = $j.datepicker.parseDate(
          $j.datepicker._defaults.dateFormat, selector.val());
      var timestamp = $j.datepicker
                          .parseDate(
                              $j.datepicker._defaults.dateFormat,
                              (new Date()).toLocaleDateString())
                          .getTime(),
          factor = (24 * 60 * 60 * 1000);
      var minDate =
              timestamp + (selector.datepicker('option', 'minDate') * factor),
          maxDate =
              timestamp + (selector.datepicker('option', 'maxDate') * factor);
      if (selectedDate.getTime() < minDate ||
          selectedDate.getTime() > maxDate) {
        return false;
      }
      return true;
    } catch (error) {
      return false;
    }
  };
  AAUI.dateRangePicker = function(selector, options) {
    var datePickerMarker = 'hasDatepicker';
    var getId = function(elemId) {
      return '#' + elemId.replace(/(:|\.|\[|\]|,)/g, '\\$1');
    };
    var _handleDateSelect = function(selectedDate, inst) {
      var $this = $j(this);
      if ($this.hasClass('jqyDepartDate')) {
        var returnField = $this.data('return-field');
        if (!returnField) {
          return;
        }
        returnField = getId(returnField);
        var dateFormat = $this.datepicker('option', 'dateFormat'),
            date = $j.datepicker.parseDate(dateFormat, selectedDate);
        var returnDate = $j(returnField).datepicker('getDate');
        if (returnDate && date > returnDate) {
          $j(returnField).datepicker('setDate', null);
        }
        $j(returnField).datepicker('option', 'minDate', date);
      }
    };
    var _highlightSelectDates = function(date) {
      try {
        var $this = $j(this), $depart, $return;
        if ($this.hasClass('jqyDepartDate')) {
          $depart = $this;
          $return = $j(getId($this.data('return-field')));
        } else {
          $depart = $j(getId($this.data('depart-field')));
          $return = $this;
        }
        var date1 = $j.datepicker.parseDate(
            $j.datepicker._defaults.dateFormat, $depart.val());
        var date2 = $j.datepicker.parseDate(
            $j.datepicker._defaults.dateFormat, $return.val());
        return [
          true,
          date1 &&
                  ((date.getTime() == date1.getTime()) ||
                   (date2 && date >= date1 && date <= date2)) ?
              'aa-highlight' :
              ''
        ];
      } catch (error) {
        return [true, ''];
      }
    };
    var _init = function(options) {
      var defaults = {
        beforeShowDay: _highlightSelectDates,
        onSelect: _handleDateSelect
      };
      var settings = $j.extend(defaults, options);
      AAUI.initDatePicker(selector, settings);
    };
    var processDateSelection = function(dateRange) {
      switch (dateRange) {
        case 'on':
          $j(selector).datepicker(
              'option', 'beforeShowDay', _highlightSelectDates);
          $j(selector).datepicker('option', 'onSelect', _handleDateSelect);
          break;
        case 'off':
          $j(selector).datepicker('option', 'beforeShowDay', null);
          $j(selector).datepicker('option', 'onSelect', null);
          break;
        default:
          break;
      }
    };
    if (options && $j(selector).hasClass(datePickerMarker)) {
      if (options.hasOwnProperty('dateRange')) {
        processDateSelection(options.dateRange);
      }
    } else {
      _init(options);
    }
  };
};
AAcom.modules.aaAutoComplete = function(AAUI) {
  AAUI.initAutoComplete = function(selector, onlyAirportsIfNotNull, options) {
    $j(selector).aaAirportAutoComplete(onlyAirportsIfNotNull, options);
    AAUI.onFocus(selector, function() {
      $j(this).prev().empty();
    });
  };
};
AAcom.modules.aaCollapse = function(AAUI) {
  AAUI.collapse = function(paramsObject) {
    var self = {}, defaults = {
      selector: null,
      target: null,
      collapsed: false,
      duration: 300,
      accessibleText: {hide: 'Hide', show: 'Show'}
    },
        options = defaults;
    for (var key in paramsObject) {
      if (paramsObject.hasOwnProperty(key)) {
        if (paramsObject[key] !== undefined) {
          options[key] = paramsObject[key];
        }
      }
    }
    var $selector = $j(options.selector), $target = $j(options.target);
    self.init = function() {
      self.setup();
      AAUI.onClick(options.selector, function(event) {
        event.preventDefault();
        self.state();
      });
    };
    self.setup = function() {
      var _selectorText = $selector.text(), _selectorFormatted = null,
          _accessibleText = options.collapsed ? options.accessibleText.show :
                                                options.accessibleText.hide;
      $target.attr({tabindex: -1, 'aria-hidden': false});
      _selectorFormatted = document.getElementById(
          options.selector.substr(1, options.selector.length));
      _selectorFormatted.outerHTML = '<a id="' +
          options.selector.substr(1, options.selector.length) + '" />';
      $selector = $j(options.selector);
      $selector.addClass('delta');
      $selector
          .attr({
            href: options.target,
            'aria-expanded': true,
            'aria-controls': options.target.substr(1, options.target.length)
          })
          .html(
              (_accessibleText ? '<span class="hidden-accessible">' +
                       _accessibleText + '</span>' :
                                 '') +
              '<span aria-hidden="true" class="' +
              (options.collapsed ? 'icon-expand' : 'icon-collapse') +
              '"></span> ' + _selectorText);
      if (options.collapsed) {
        self.state();
      }
    };
    self.state = function() {
      $target.stop().animate({height: 'toggle'}, {
        duration: options.duration,
        complete: function() {
          $j(this).attr('aria-hidden', options.collapsed ? true : false);
          $selector.attr('aria-expanded', options.collapsed ? false : true);
          $selector.children('.hidden-accessible')
              .text(
                  options.collapsed ? options.accessibleText.show :
                                      options.accessibleText.hide);
          $selector.children('[class^="icon-"]')
              .attr(
                  'class', options.collapsed ? 'icon-expand' : 'icon-collapse');
          options.collapsed = !options.collapsed;
        }
      });
    };
    return self;
  };
};
AAcom.modules.aaTooltip = function(AAUI) {
  AAUI.initTooltip = function(element, options) {
    if ($j.isFunction($j.fn.aaTooltip)) {
      $j(element).aaTooltip(options);
    }
  };
};
AAcom.modules.aaToggle = function(AAUI) {
  AAUI.initToggle = function(element, options) {
    if ($j.isFunction($j.fn.aaToggle)) {
      $j(element).aaToggle(options);
    }
  };
};
AAcom.modules.aaBusy = function(AAUI) {
  AAUI.initBusy = function(element, options) {
    if ($j.isFunction($j.fn.aaBusy)) {
      $j(element).aaBusy(options).start();
    }
  };
  AAUI.stopBusy = function(element) {
    if ($j.isFunction($j.fn.aaBusy)) {
      $j(element).aaBusy().stop();
    }
  };
};
AAcom.modules.aaCarousel = function(AAUI) {
  var self = {};
  AAUI.initBusy('.flexslider-container', {showlogo: false});
  AAUI.initCarousel = function(element, options) {
    if ($j.isFunction($j.fn.aaCarousel)) {
      self = $j(element).aaCarousel(options);
      if (self) {
        self.initCarousel();
      }
      AAUI.stopBusy('.flexslider-container');
    }
  };
  AAUI.moveSliderRight = function() {
    if (self) {
      self.moveSliderRight();
    }
  };
};
AAcom.modules.aaPinning = function(AAUI) {
  var self = {};
  AAUI.initPinElement = function(options) {
    if ($j.isFunction($j.aaPinning)) {
      self = $j.aaPinning();
      self.affix({
        element: options.element,
        offset: options.offset,
        supportLandscapeOrientation: options.orientation
      });
    }
  };
};