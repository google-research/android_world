var ct = '<img src=';
var cu = '/content/images/common/wa.gif?Log=1';
var cu2 = '/content/images/common/wa2.gif?Log=1';
var ce = '>';
function KeyValueObject(key, value) {
  this.key = key;
  this.value = value;
}
jQuery(document).ready(function() {
  if (jQuery.aaCookie != null && jQuery.aaCookie.get('aawaScreenRes') == null) {
    jQuery.aaCookie.set('aawaScreenRes', 'done', null, '/');
    var d = {};
    d.dt = document.title;
    d.dr = document.referrer;
    d.sw = screen.width;
    d.sh = screen.height;
    d.cd = screen.colorDepth;
    d.cb = new Date().getTime();
    var vo = '';
    if (typeof v != 'undefined') {
      for (vKey in v) {
        vo = vo + '&' + vKey + '=' + escape(v[vKey]);
      }
    }
    for (dKey in d) {
      vo = vo + '&' + dKey + '=' + escape(d[dKey]);
    }
    img = new Image();
    img.src = cu + vo;
  }
  captureLink();
});
function calcTotalNoOfPsgrs(currForm) {
  var numPsgrs = 0;
  if (currForm.seniorPassengerCount.value == null) {
    currForm.seniorPassengerCount.value = 0;
  }
  if (currForm.youngAdultPassengerCount.value == null) {
    currForm.youngAdultPassengerCount.value = 0;
  }
  if (currForm.childPassengerCount.value == null) {
    currForm.childPassengerCount.value = 0;
  }
  if (currForm.infantPassengerCount.value == null) {
    currForm.infantPassengerCount.value = 0;
  }
  if (currForm.adultPassengerCount.value == null) {
    currForm.adultPassengerCount.value = 0;
  }
  numPsgrs = parseInt(currForm.adultPassengerCount.value) +
      parseInt(currForm.seniorPassengerCount.value) +
      parseInt(currForm.childPassengerCount.value) +
      parseInt(currForm.infantPassengerCount.value) +
      parseInt(currForm.youngAdultPassengerCount.value);
  if (currForm.seniorPassengerCount.value == null) {
    currForm.seniorPassengerCount.value = 0;
  }
  if (currForm.youngAdultPassengerCount.value == null) {
    currForm.youngAdultPassengerCount.value = 0;
  }
  if (currForm.childPassengerCount.value == null) {
    currForm.childPassengerCount.value = 0;
  }
  if (currForm.infantPassengerCount.value == null) {
    currForm.infantPassengerCount.value = 0;
  }
  if (currForm.adultPassengerCount.value == null) {
    currForm.adultPassengerCount.value = 0;
  }
  currForm.passengerCount.value = numPsgrs;
}
function calcTotalNoOfPsgrsOnHomePage(strHotel) {
  var value;
  if (strHotel != null && strHotel.length > 0) {
    value =
        jQuery('#flightSearchForm\\.adultPassengerCount\\.flightHotel').val();
  } else {
    value = jQuery('#flightSearchForm\\.adultOrSeniorPassengerCount').val();
  }
  if (value == null) {
    value = '0';
  }
  numPsgrs = parseInt(value);
  jQuery('#flightSearchForm\\.passengerCount').val(numPsgrs);
  var numSeniors = jQuery('#flightSearchForm\\.seniorPassengerCount').val();
  jQuery('#flightSearchForm\\.adultPassengerCount').val(numPsgrs - numSeniors);
}
function trackAllFormValues(form) {
  var reservationForm = 'reservationFlightSearchForm';
  var multiCityForm = 'multiFlightSearchForm';
  if (form.action) {
    var vo = '&v_formAction=' + escape(form.action);
  } else {
    var vo = '&v_formAction=NONE';
  }
  if (form.id == reservationForm) {
    form.flightSearch.value = 'revenue';
    var airPassVar = false;
    try {
      if (form.aairpassSearchType[0].checked == true) {
        form.aairpassSearchType[1].value = 'true';
        airPassVar = true;
      }
    } catch (ex) {
    }
    if (form.multi_success.disabled == false) {
      form.flightSearch.value = 'ClickToMultiCity';
    } else {
      if (form.dates_flex_success.disabled == false) {
        form.flightSearch.value = 'ClickToDatesFlexible';
      } else {
        if (airPassVar == true) {
          form.flightSearch.value = 'aairpass';
        } else {
          if (jQuery('#flightSearchForm\\.tripType\\.redeemMiles')
                  .attr('checked')) {
            form.flightSearch.value = 'award';
          }
        }
      }
    }
    if (jQuery('#flightSearchForm\\.tripType\\.roundTrip').attr('checked') ||
        jQuery('#flightSearchForm\\.tripType\\.oneWay').attr('checked')) {
      vo += '&v_air_room_car=A';
    }
    if (jQuery('#round-trip-hotel').attr('checked')) {
      vo += '&v_air_room_car=AR';
    }
  } else {
    if (form.id == multiCityForm) {
      vo += '&v_jsEnabledPathName=MultiCity';
    }
  }
  for (i = 0; i < form.length; i++) {
    if (form.elements[i].disabled == false) {
      if (form.elements[i].type == 'checkbox') {
        if (form.elements[i].checked) {
          var item = form.elements[i];
          var formitem = 'v_' + item.name;
          var formvalue = item.value;
          if (item.name != '') {
            vo += '&' + formitem + '=' + formvalue;
          }
        }
      } else {
        if (form.elements[i].type == 'radio') {
          if (form.elements[i].checked) {
            var item = form.elements[i];
            var formitem = 'v_' + item.name;
            var formvalue = item.value;
            if (item.name != '') {
              vo += '&' + formitem + '=' + formvalue;
              if (item.name == 'searchTypeMode' || item.name == 'searchType') {
                var jsreportvar = '';
                if (formvalue == 'matrix') {
                  jsreportvar = 'SearchByPriceAndSchedule';
                } else {
                  if (formvalue == 'schedule') {
                    jsreportvar = 'SearchBySchedule';
                  }
                }
                vo += '&v_jsEnabledPathName=' + jsreportvar;
              }
            }
          }
        } else {
          if (form.elements[i].type == 'select') {
            var item = form.elements[i];
            var formitem = 'v_' + item.name;
            var optionindex = eval(form.elements[i].selectedIndex);
            var formvalue = form.elements[i].options[optionindex].value;
            if (item.name != '') {
              vo += '&' + formitem + '=' + formvalue;
            }
          } else {
            var item = form.elements[i];
            var formitem = 'v_' + item.name;
            var formvalue = item.value;
            if (form.id == reservationForm) {
              if (formitem == 'v_hotelRoomCount') {
                formitem = 'v_rooms';
              }
              if (formitem == 'v_serviceclass') {
                vo += '&v_cabinOfServicePreference=' + formvalue;
              }
              if (formitem == 'v_moreOptionsIndicator') {
                formitem = '';
              }
            }
            if (item.name != '' && formitem != '') {
              vo += '&' + formitem + '=' + formvalue;
            }
          }
        }
      }
    }
  }
  img = new Image();
  img.src = cu + vo;
}
function trackDestinationIdeas() {
  var dt = new Date();
  var vo = '&v_destination=Y&v_=' + dt.getTime();
  img = new Image();
  img.src = cu + vo;
  return true;
}
function trackLogin(loginForm) {
  var vo = '&v_formAction=' + escape(loginForm.action);
  if (loginForm.aadvantageNumber) {
    vo += '&v_aadvNum=' + loginForm.aadvantageNumber.value;
  }
  img = new Image();
  img.src = cu + vo;
  return true;
}
function trackToggleLocale(toggleButton) {
  var vo = '&v_formAction=' + escape(toggleButton.form.action);
  vo += '&v_event=toggleLocale';
  vo += '&v_toLanguage=' + toggleButton.value;
  img = new Image();
  img.src = cu + vo;
  return true;
}
function trackEvent(eventName) {
  var vo = '&v_event=' + eventName;
  img = new Image();
  img.src = cu + vo;
  return true;
}
function trackEventAndPageView(eventName, pageViewName) {
  var vo = '&v_event=' + eventName + '&v_pageview=' + pageViewName;
  img = new Image();
  img.src = cu + vo;
  return true;
}
function trackCheckInEventAndErrorCode(errorCode) {
  var vo = '&v_fciEvent=Flight Check In Failure&v_errorCode=' + errorCode;
  img = new Image();
  img.src = cu + vo;
  return true;
}
function trackJbSeatEvent(eventName) {
  var vo = '&' + eventName;
  img = new Image();
  img.src = cu + vo;
  return true;
}
function trackCityEvent(eventName) {
  var vo = '&v_event=Airport lookup event&v_airportCityCode=' + eventName;
  img = new Image();
  img.src = cu + vo;
  return true;
}
function trackDistanceEvent(eventName) {
  var vo =
      '&v_event=Airport lookup -Airport Distance Selected&v_lookup_distance=' +
      eventName;
  img = new Image();
  img.src = cu + vo;
  return true;
}
function trackPreOrderData(
    totalPax, saladCount, sandwichCount, numberOfDaysForOutboundSegment,
    numberOfDaysForInboundSegment, numberOfPaxWithNone) {
  var vo = '&v_PreOrderTotalPassengers=' + totalPax +
      '&v_PreOrderTotalSalads=' + saladCount +
      '&v_PreOrderTotalSandwiches=' + sandwichCount +
      '&v_PreOrderDaysFromDepartureForFirstSegment=' +
      numberOfDaysForOutboundSegment +
      '&v_PreOrderDaysFromDepartureForSecondSegment=' +
      numberOfDaysForInboundSegment +
      '&v_PreOrderTotalNones =' + numberOfPaxWithNone;
  img = new Image();
  img.src = cu + vo;
  return true;
}
function addEvent(obj, evType, fn) {
  if (obj.addEventListener) {
    obj.addEventListener(evType, fn, false);
    return true;
  } else {
    if (obj.attachEvent) {
      var r = obj.attachEvent('on' + evType, fn);
      return r;
    } else {
      return false;
    }
  }
}
function captureLink() {
  if (document.links[0]) {
    if (document.links) {
      var links = document.links, link, k = 0;
      while (link = links[k++]) {
        if ((link.href.charAt(0) == '#') ||
            (link.href.indexOf('javascript:void') != -1) ||
            (link.href.indexOf(document.domain) != -1)) {
          continue;
        }
        if (link.href.indexOf('phx.corporate-ir.net') == -1) {
          if (!link.onclick) {
            link.onclick = captureLinkHref;
          }
        }
      }
    }
  }
}
function captureLinkHref() {
  var lc = new Image();
  this.parent = this.parentNode;
  lc.src = cu + '&v_externalLinkClick=' + escape(this.href) +
      '&v_fromLocation=' + escape(document.location) +
      '&cd=' + new Date().getTime();
  return true;
}
function captureExtLink(toLink, fromLocation) {
  var lc = new Image();
  lc.src = cu + '&v_externalLinkClick=' + escape(toLink) +
      '&v_fromLocation=' + escape(fromLocation) + '&cd=' + new Date().getTime();
  return true;
}
function captureExtClickThru(
    clickThruLink, reportedLocation, reportedTitle, repository, contentId,
    locale, flash) {
  var lc = new Image();
  lc.src = cu + '&url=' + escape(clickThruLink) +
      '&anchorLocation=' + escape(reportedLocation) +
      '&reportedTitle=' + escape(reportedTitle) +
      '&repositoryName=' + escape(repository) +
      '&repositoryId=' + escape(contentId) + '&_locale=' + escape(locale) +
      '&flash=' + escape(flash) + '&cd=' + new Date().getTime();
  return true;
}
function captureExtClickThru(
    clickThruLink, reportedLocation, reportedTitle, repository, contentId,
    locale, flash, reportedPosition) {
  var lc = new Image();
  lc.src = cu + '&url=' + escape(clickThruLink) +
      '&anchorLocation=' + escape(reportedLocation) +
      '&reportedTitle=' + escape(reportedTitle) +
      '&repositoryName=' + escape(repository) +
      '&repositoryId=' + escape(contentId) + '&_locale=' + escape(locale) +
      '&flash=' + escape(flash) + '&reportedPosition=' + reportedPosition +
      '&cd=' + new Date().getTime();
  return true;
}
function trackBrazilInstallmentsLearnMoreEvent(eventName) {
  var vo = '&v_event=' + eventName;
  img = new Image();
  img.src = cu + vo;
  return true;
}
function trackEvent(eventName, countryCode) {
  var vo = '';
  if (eventName != null) {
    vo += '&v_event=' + eventName;
    if (countryCode != null) {
      vo += '&v_FSNCountry=' + countryCode;
    }
    img = new Image();
    img.src = cu + vo;
  }
  return true;
}
function trackMyAccountEvents(eventName) {
  var vo = '&v_event=' + eventName;
  img = new Image();
  img.src = cu + vo;
  return true;
}
function trackMyResEvents(eventName) {
  var vo = '&v_event=' + eventName;
  img = new Image();
  img.src = cu2 + vo;
  return true;
}
function trackSeveralKeyValues(keyValuePairsArray) {
  var vo = '';
  for (var i = 0; i < keyValuePairsArray.length; i++) {
    vo += '&' + keyValuePairsArray[i].key + '=' + keyValuePairsArray[i].value;
  }
  var img = new Image();
  img.src = cu + vo;
  return true;
}
function trackKeyValue(key, value) {
  var vo = '&' + key + '=' + value;
  var img = new Image();
  img.src = cu + vo;
  return true;
}