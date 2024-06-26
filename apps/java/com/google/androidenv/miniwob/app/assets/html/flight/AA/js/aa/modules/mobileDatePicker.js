AAcom.modules.aaMobileDatePicker = function(AAUI) {
  var module, $datePicker, $aaDialog, currentDate, onSelect, settings, $target,
      $start, $end, dateRange = {start: null, end: null};
  $j.extend($j.datepicker, {
    _inlineDatepicker2: $j.datepicker._inlineDatepicker,
    _inlineDatepicker: function(target, inst) {
      this._inlineDatepicker2(target, inst);
      var beforeShow = $j.datepicker._get(inst, 'beforeShow');
      if (beforeShow) {
        beforeShow.apply(target, [target, inst]);
      }
    }
  });
  var _altField = function(selector) {
    $target = $j(selector);
    return this;
  };
  var _hide = function() {
    $aaDialog.closeDialog();
  };
  var _getDate = function() {
    return currentDate;
  };
  var _onSelectHandler = function(onSelectFunc) {
    onSelect = onSelectFunc;
    return this;
  };
  var _show = function() {
    $aaDialog.openDialog();
    if ($target.val() || $start.val() || $end.val()) {
      var offset;
      if ($target.prop('id') == $start.prop('id') && $start.val() === '' &&
          $end.val() !== '') {
        offset = $j('td.ui-date-range').offset();
      } else {
        offset =
            $j('a.ui-state-active').closest('div.ui-datepicker-group').offset();
      }
      if (offset) {
        $j(document).scrollTop(offset.top - 41);
      }
    }
  };
  var _setDate = function(date) {
    var format, value, currentDateValue = $datePicker.datepicker('getDate');
    if (date) {
      format = $datePicker.datepicker('option', 'dateFormat');
      try {
        value = $j.datepicker.parseDate(format, date);
        if (value && value.getTime() !== currentDateValue.getTime()) {
          $datePicker.datepicker('setDate', date);
        }
      } catch (ex) {
      }
    } else {
      $datePicker.find('a.ui-state-active')
          .removeClass('ui-state-highlight ui-state-active ui-state-hover');
      $datePicker.find('td.ui-datepicker-current-day')
          .removeClass('ui-datepicker-current-day');
    }
  };
  var _setRange = function(range) {
    $j.extend(dateRange, range);
    return this;
  };
  var _setTitle = function(title) {
    if (typeof title === 'string') {
      $j('#datePickerDialog').dialog('option', 'title', title);
    }
    return this;
  };
  var beforeShowDay = function(date) {
    if ((dateRange.start === null && dateRange.end === null) || date === null) {
      return [true, ''];
    }
    var css = '', currentDateTime = date.getTime(),
        startDateTime = dateRange.start ? dateRange.start.getTime() : null,
        endDateTime = dateRange.end ? dateRange.end.getTime() : null;
    if (endDateTime && currentDateTime > endDateTime) {
      return [true, ''];
    }
    if (startDateTime === currentDateTime) {
      css = 'ui-date-selected';
      if (endDateTime && endDateTime !== startDateTime) {
        css += ' -start';
      }
      return [true, css];
    }
    if (endDateTime === currentDateTime) {
      css = 'ui-date-selected';
      if (startDateTime && startDateTime !== endDateTime) {
        css += ' -end';
      }
      return [true, css];
    }
    if (startDateTime && endDateTime && currentDateTime > startDateTime &&
        currentDateTime < endDateTime) {
      return [true, 'ui-date-include'];
    }
    if (endDateTime && currentDateTime < endDateTime &&
        endDateTime - 3628800000 == currentDateTime) {
      css = ' ui-date-range';
    }
    return [true, css];
  };
  var validateDateRange = function() {
    var departDate = dateRange.start, returnDate = dateRange.end;
    if (returnDate && departDate && departDate > returnDate) {
      dateRange.end = null;
      $end.val('');
      updateMinDate();
    }
  };
  var getElemSelector = function(rangeOption) {
    var elemSelector = '';
    if (typeof rangeOption === 'object' && rangeOption.start &&
        rangeOption.end) {
      elemSelector = rangeOption.start + ',' + rangeOption.end;
    }
    return elemSelector;
  };
  var getId = function(elemId) {
    return '#' + elemId.replace(/(:|\.|\[|\]|,)/g, '\\$1');
  };
  var isDateRange = function() {
    return $start && $end;
  };
  var onSelectDate = function(dateText, inst) {
    $target.val(dateText);
    currentDate = $datePicker.datepicker('getDate');
    if (isDateRange()) {
      updateDateRange();
    }
    if (onSelect) {
      onSelect.apply($target, [dateText, inst]);
    }
    _hide();
    $j(window).scrollTop($target.offset().top - 100);
  };
  var setDateRange = function() {
    try {
      var value, format = $datePicker.datepicker('option', 'dateFormat');
      value = $start.val();
      dateRange.start = value ? $j.datepicker.parseDate(format, value) : null;
      value = $end.val();
      dateRange.end = value ? $j.datepicker.parseDate(format, value) : null;
    } catch (ex) {
      dateRange.start = null;
      dateRange.end = null;
      $start.val('');
      $end.val('');
    }
  };
  var setupDateRange = function(rangeOption) {
    if (typeof rangeOption !== 'object') {
      return;
    }
    if (rangeOption.start) {
      $start = $j(rangeOption.start);
    }
    if (rangeOption.end) {
      $end = $j(rangeOption.end);
    }
    setDateRange();
  };
  var updateDateRange = function() {
    setDateRange();
    validateDateRange();
    updateMinDate();
  };
  var updateMinDate = function() {
    $datePicker.datepicker('option', 'minDate', settings.minDate);
    $datePicker.datepicker('option', 'numberOfMonths', settings.numberOfMonths);
    var minDate = $datePicker.datepicker('option', 'minDate'),
        maxDate = $datePicker.datepicker('option', 'maxDate'),
        numberOfMonths = settings.numberOfMonths;
    if (dateRange.start && $target.prop('id') === $end.prop('id')) {
      if (minDate === 0 || minDate.getTime() != dateRange.start.getTime()) {
        $datePicker.datepicker('option', 'minDate', dateRange.start);
        if (maxDate === 0) {
          var startDateMonth = dateRange.start.getMonth();
          $datePicker.datepicker(
              'option', 'numberOfMonths', numberOfMonths - startDateMonth);
        }
      }
      return;
    }
  };
  var init = function(selector, options) {
    var rangeOptions = {start: '', end: ''};
    if (typeof selector === 'object') {
      $j.extend(rangeOptions, selector.dateRange);
      if (!rangeOptions.start || !rangeOptions.end) {
        return;
      }
      selector = getElemSelector(rangeOptions);
    }
    var $selector = $j(selector);
    if (!$selector.length) {
      return;
    }
    if (!$j('#datePickerDialog').length) {
      return;
    }
    var aaUtil = new aa_Utilities(), $mainSection = $j('#main');
    $aaDialog = aaUtil.aaDialog('datePicker', {
      modal: false,
      width: '100%',
      hide: 500,
      toggleScroll: true,
      resizable: false,
      aaPosition: {vertical: 'top', horizontal: null, of: window},
      cssClass: 'aa-ui-dialog',
      draggable: false,
      onOpen: function() {
        $mainSection.hide();
        noBounce.init({
          animate: true,
          element: jQuery('.aa-ui-dialog .ui-dialog-content').get(0)
        });
      },
      onBeforeClose: function() {
        $mainSection.show();
      }
    });
    $datePicker = $j('#inlineCalendar');
    settings = {
      inline: true,
      minDate: 0,
      maxDate: '+331d',
      numberOfMonths: 12,
      showButtonPanel: false,
      onSelect: onSelectDate,
      beforeShowDay: beforeShowDay,
      beforeShow: function(input, inst) {
        inst.dpDiv.find('a.ui-state-active')
            .removeClass('ui-state-highlight ui-state-active ui-state-hover');
        inst.dpDiv.find('td.ui-datepicker-current-day')
            .removeClass('ui-datepicker-current-day');
      }
    };
    $j.extend(settings, options);
    $datePicker.datepicker(settings);
    setupDateRange(rangeOptions);
    $j(selector).on('focus', function() {
      $target = $j(this);
      $target.blur();
      _setTitle($target.data('title'));
      if (isDateRange()) {
        updateMinDate();
      }
      _setDate($target.val());
      _show();
      return false;
    });
    $j.each($selector, function(index) {
      var calendarIcon =
          $j('<button />')
              .attr({
                type: 'button',
                'data-altfield': this.id,
                'class': 'ui-datepicker-trigger'
              })
              .append(
                  '<span class=\'hidden-accessible\'>' +
                  AAUI.getProperty('calendar.hiddenText') + '</span>');
      calendarIcon.on('click', function() {
        var $this = $j(this);
        var altField = $this.data('altfield');
        var targetId = getId(altField);
        _altField(targetId);
        var $dateInput = $j(targetId);
        _setTitle($dateInput.data('title'));
        if (isDateRange()) {
          updateMinDate();
        }
        _setDate($dateInput.val());
        _show();
        return false;
      });
      $j(this).after(calendarIcon);
    });
  };
  AAUI.initMobileDatePicker = function(selector, options) {
    init(selector, options);
    module = {
      altField : _altField,
      getDate : _getDate,
      hide : _hide,
      onSelect : _onSelectHandler,
      setRange : _setRange,
      setTitle : _setTitle,
      show : _show
    };
    return module;
  };
};