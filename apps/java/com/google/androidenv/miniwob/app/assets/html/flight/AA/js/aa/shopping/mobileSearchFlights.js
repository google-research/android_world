AAcom(
    'browserdetect', 'utilities', 'ajax', 'commonsetup', 'aaAutoComplete',
    'aaMobileDatePicker', function(AAUI) {
      $j(function() {
        var search = (function($j, device, cache) {
          var tripType = {
            RoundTrip: 'roundTrip',
            OneWay: 'oneWay',
            MultiCity: 'multi',
          };
          var MAX_PAX = 6, FLIGHT_SEARCH_FORM_CACHE_KEY = 'flightSearchView',
              selectedTripType = tripType.RoundTrip,
              tripTypeNavTabMappings =
                  [tripType.RoundTrip, tripType.OneWay, tripType.MultiCity],
              isSecure = AAUI.getProperty('account.isSecure') == 'true',
              isAirpass = cache.get('#airpass\\.useAirpass1').prop('checked'),
              homeTownAirport = AAUI.getProperty('HomeTownAirport'),
              $flightSearchForm = $j('#flightSearchView'),
              loadingTxt = AAUI.getProperty('LoadingText');
          var getTripType = function(selectedTabIndex) {
            return tripTypeNavTabMappings[selectedTabIndex];
          };
          var setTripType = function(selectedTabIndex) {
            selectedTripType = getTripType(selectedTabIndex);
            cache.get('#tripType').val(selectedTripType);
          };
          var getCurrentTripType = function() {
            return selectedTripType;
          };
          var tripTypeValueToInt = function(selectedTripType) {
            switch (selectedTripType) {
              case tripType.OneWay:
                return 1;
              case tripType.MultiCity:
                return 2;
            }
            return 0;
          };
          var toggleCheckbox = function(isChecked, target, container) {
            if (isChecked) {
              cache.get(target).prop('checked', false);
              cache.get(container).hide();
            } else {
              cache.get(container).show();
            }
          };
          var render = function() {
            switch (getCurrentTripType()) {
              case tripType.RoundTrip:
                cache.get('#departDateSection')
                    .removeClass('span-phone12')
                    .addClass('span-phone6');
                break;
              case tripType.OneWay:
                cache.get('#departDateSection')
                    .removeClass('span-phone6')
                    .addClass('span-phone12');
                cache.get('#segments1\\.travelDate').val('');
                break;
            }
          };
          var submitHandler = function() {
            if (getCurrentTripType() === tripType.RoundTrip ||
                getCurrentTripType() === tripType.OneWay) {
              if ($j('body')
                      .aaBusy({message: loadingTxt, form: this})
                      .start()) {
                return false;
              }
            }
          };
          var initFlightSearchTab = function() {
            $j('#flight-tabs').tabs({
              active: tripTypeValueToInt(selectedTripType),
              activate: function(event, ui) {
                setTripType(ui.newTab.index());
                render(true);
              }
            });
          };
          var setDefaultOrigin = function() {
            if (homeTownAirport.length &&
                cache.get('#segments0\\.destination').val().length <= 0) {
              cache.get('#segments0\\.origin').val(homeTownAirport);
            }
          };
          var restoreSavedSearch = function() {
            if (sessionStorage && isFromLogin()) {
              var flightForm =
                  sessionStorage.getItem(FLIGHT_SEARCH_FORM_CACHE_KEY);
              if (flightForm) {
                var params = flightForm.split('&'), max = params.length, i = 0,
                    elem, nameValuePair = [], name, value;
                while (i < max) {
                  nameValuePair = params[i].split('=');
                  if (nameValuePair.length < 1) {
                    i++;
                    continue;
                  }
                  name = unescape(nameValuePair[0]);
                  value = unescape(nameValuePair[1]);
                  elem = cache.get('[name=\'' + name + '\']');
                  if (elem.length) {
                    switch (elem.prop('type')) {
                      case 'checkbox':
                        elem.prop('checked', value);
                        break;
                      case 'radio':
                        var index = elem.length;
                        while (index--) {
                          if (elem[index].value === value) {
                            elem[index].checked = true;
                            break;
                          }
                        }
                        break;
                      default:
                        elem.val(value);
                        if (name == 'tripType') {
                          selectedTripType = value;
                        }
                        break;
                    }
                  }
                  i++;
                }
                toggleCheckbox(
                    cache.get('#airpass\\.useAirpass1').prop('checked'),
                    '#refundable1', '#refundableSection');
                toggleCheckbox(
                    cache.get('#refundable1').prop('checked'),
                    '#airpass\\.useAirpass1', '#airpassSection');
              }
              sessionStorage.removeItem(FLIGHT_SEARCH_FORM_CACHE_KEY);
            }
          };
          var isFromLogin = function() {
            var referrer = document.referrer;
            return referrer && referrer.indexOf('/loyalty/login') > -1;
          };
          var initAccountLogin = function() {
            $j('#loginLogoutLink, #logInAdvantageLink').click(function(e) {
              e.preventDefault();
              try {
                if (sessionStorage) {
                  sessionStorage.setItem(
                      FLIGHT_SEARCH_FORM_CACHE_KEY,
                      $flightSearchForm.serialize());
                }
              } catch (error) {
              }
              if (isSecure) {
                deleteVirtualPNR();
                window.location.href = this.href;
                return;
              }
              deleteVPNRModal();
            });
          };
          var initView = function() {
            $j('body').aaBusy().stop();
            selectedTripType = cache.get('#tripType').val();
            cache.get('#segments0\\.travelDate').prop('readonly', true);
            cache.get('#segments1\\.travelDate').prop('readonly', true);
            if (isSecure) {
              cache.get('#airpass\\.useAirpass1').on('click', function() {
                toggleCheckbox(
                    this.checked, '#refundable1', '#refundableSection');
              });
              cache.get('#refundable1').on('click', function() {
                toggleCheckbox(
                    this.checked, '#airpass\\.useAirpass1', '#airpassSection');
              });
            }
            var options = {
              dateRange: {
                start: '#segments0\\.travelDate',
                end: '#segments1\\.travelDate'
              }
            };
            AAUI.initMobileDatePicker(options);
            AAUI.initAutoComplete(
                '.aaAutoComplete', false, {position: {collision: 'flip'}});
            $flightSearchForm.on('submit', submitHandler);
            $j(window).bind('pageshow', function(event) {
              if (event.originalEvent.persisted) {
                window.location.reload();
              }
            });
          };
          var init = function() {
            initView();
            initFlightSearchTab();
            initAccountLogin();
            setDefaultOrigin();
            restoreSavedSearch();
            render();
          };
          return {init: init};
        })(jQuery.noConflict(), $device, aaCache);
        search.init();
      });
    });