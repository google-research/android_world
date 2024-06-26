function getTotalFareAmount() {
  for (var n,
       i = 0,
       r = Alaska.$('flights-form').getElementsByClassName('fareSelected'),
       t = 0;
       t < r.length; t++)
    n = r[t].getAttribute('data-p'),
    n != null && n != '' && (i += parseFloat(n));
  return i
}
function CurrencyConversion(n) {
  var i, t, a, c, l, v;
  if (divContainer = n ? Alaska.$('modal-window') : Alaska.$('CurConverter'),
      i = divContainer.getElementsByClassName('amount'), t = i[0].value,
      t.trim() == '' || isNaN(t) || parseFloat(t) == 0)
    return Alaska.util.addClass(i[0], 'input-validation-error'),
           divContainer.getElementsByClassName('form-error-msg')[0]
               .style.display = 'block',
           divContainer.getElementsByClassName('results')[0].style.display =
               'none',
           !1;
  t = t.trim();
  Alaska.util.removeClass(i[0], 'input-validation-error');
  divContainer.getElementsByClassName('form-error-msg')[0].style.display =
      'none';
  divContainer.getElementsByClassName('results')[0].style.display = 'block';
  var r = divContainer.getElementsByClassName('fromCurrList')[0],
      u = r.options[r.selectedIndex].getAttribute('data-cc'),
      s = r.options[r.selectedIndex].getAttribute('data-ex'),
      f = divContainer.getElementsByClassName('toCurrList')[0],
      e = f.options[f.selectedIndex].getAttribute('data-cc'),
      h = f.options[f.selectedIndex].getAttribute('data-ex'), o = 0;
  o = u == 'USD' ? parseFloat(t) * parseFloat(h) :
      e == 'USD' ? parseFloat(t) / parseFloat(s) :
                   parseFloat(t) / parseFloat(s) * parseFloat(h);
  o = numberWithCommas(o.toFixed(2));
  strConvAmt = o.toString();
  strConvAmt = strConvAmt.replace('.00', '');
  a = t + ' (' + u + ') = ' + strConvAmt + ' (' + e + ')';
  divContainer.getElementsByClassName('convResult')[0].innerHTML = a;
  c = divContainer.getElementsByClassName('rateUsedLabel');
  l = divContainer.getElementsByClassName('rateUsed');
  e == u ? (c[0].innerHTML = '', l[0].innerHTML = '') :
           (c[0].innerHTML = 'Conversion rate:',
            v = ' ' + s + ' ' + u + ' = ' + h + ' ' + e, l[0].innerHTML = v)
}
function InitSearch() {
  var r, t, f, i, o;
  if (areCookiesEnabled() || Alaska.util.showClientMsg(enableCookiesMsg),
      r = decodeURIComponent(readCookie('Search')),
      r != 'null' && r.indexOf('|') >= 0) {
    var n = r.split('|'), u = Alaska.$('departure-date'),
        e = formatDate(new Date);
    for ((u.value == '' || u.value == e) &&
             (u.value = n[3], u.value.length > 0),
         n[0] == 'r' ?
             (t = Alaska.$('return-date'),
             (t.value == '' || t.value == e) &&
                  (t.value = n[4], t.value.length > 0)) :
             Alaska.$('srh-isow').checked = !0,
             Alaska.toggleSearch(Alaska.$('srh-isow')),
             Alaska.$('geo-from').value = n[1].replace(/~/g, ','),
             Alaska.$('geo-to').value = n[2].replace(/~/g, ','),
             Alaska.$('num-travelers').value =
                 Alaska.$('tnum-display').innerHTML = n[5],
             f = document.getElementsByName('SearchFields.UpgradeOption'),
             i = 0, o = f.length;
         i < o; i++)
      if (f[i].value == n[6]) {
        f[i].click();
        break
      }
    Alaska.$('srh-is-miles').checked = n[7] === 'true' ? !0 : !1;
    Alaska.$('discount-code').value = n[8];
    Alaska.$('is-cal') != null && n[9] === 'true' &&
        (Alaska.$('is-cal').checked = !0)
  }
  Alaska.toggleMiles(Alaska.$('srh-is-miles'));
  DiscountCodeDropCheck();
  Alaska.toggleCal(Alaska.$('is-cal'))
}
function formatDate(n) {
  return n.getMonth() + 1 + '/' + n.getDate() + '/' + n.getFullYear()
}
function sortResult(n, t) {
  var r, f, u, e, i;
  for (Alaska.spinner.show(),
       r = Alaska.$('result-' + t).getElementsByClassName('sliceoption'),
       f = r.length, createCookie('SortBy' + t, n), u = Create2DArray(f), i = 0;
       i < f; i++)
    e = r[i].getAttribute('data-s' + n), u[i][0] = parseInt(e),
    u[i][1] = r[i].outerHTML;
  for (u.sort(function(n, t) {
         var i = n[0], r = t[0];
         return i == r ? 0 : i < r ? -1 : 1
       }),
       i = 0;
       i < f; i++)
    r[i].outerHTML = u[i][1];
  setTimeout(function() {
    Alaska.spinner.hide()
  }, 250)
}
function Create2DArray(n) {
  for (var i = [], t = 0; t < n; t++) i[t] = [];
  return i
}
function InitShopping() {
  function e(n) {
    var t = Alaska.$('SortOption' + n);
    t.value = readCookie('SortBy' + n)
  }
  function o(n) {
    var t = Alaska.$('filter-bar' + n), i = Alaska.$('filter-cnt' + n);
    readCookie('ShowFilter' + n) == 0 ?
        (t.className = 'filter-bar', i.style.display = 'none') :
        (t.className = 'filter-bar-open', i.style.display = 'block')
  }
  var n = readCookie('DepOptId'), t = readCookie('DepFare'), i, r, u, f, s, h;
  n != null && n != '-1' && selectOption(t, 0, n, 0, 0);
  n = readCookie('RetOptId');
  t = readCookie('RetFare');
  n != null && n != '-1' && selectOption(t, 1, n, 0, 0);
  sortResult(readCookie('SortBy0'), 0);
  e(0);
  o(0);
  i = readCookie('Cabin0');
  i != null && (Alaska.$('filter-cabin0').value = i);
  Alaska.$('result-1') &&
      (sortResult(readCookie('SortBy1'), 1), e(1), o(1),
       r = readCookie('Cabin1'),
       r != null && (Alaska.$('filter-cabin1').value = r));
  u = readCookie('ShowAllDep');
  u != null && u != '' && showAllFlights(0);
  f = readCookie('ShowAllRet');
  f != null && f != '' && showAllFlights(1);
  Alaska.filterCabin(Alaska.$('filter-cabin0').value, 0);
  Alaska.$('filter-cabin1') &&
      Alaska.filterCabin(Alaska.$('filter-cabin1').value, 1);
  s = document.getElementsByClassName('server-msg-error');
  s.length == 0 ? (h = readCookie('VrtPos'), window.scrollTo(0, h)) :
                  window.scrollTo(0, 0)
}
function ClearErrors(n) {
  var i = document.getElementsByClassName(n), t;
  if (i.length > 0)
    while (t = i[0]) t.parentNode.removeChild(t)
}
function ClearDivErrors(n, t) {
  var u = Alaska.$(n), i, r;
  if (u.innerHTML.indexOf(t) > -1 &&
      (i = u.getElementsByClassName(t), i.length > 0))
    while (r = i[0]) r.parentNode.removeChild(r)
}
function selectOption(n, t, i, r, u) {
  var l, e;
  if (i != -1) {
    var p = 'fare-' + t + '-' + i + '-' + n, h = 'result-' + t,
        w = 'option-' + t + '-' + i, b = 'showall' + t, a = 'filter-cabin' + t,
        v = readCookie('Cabin' + t), f = !1, o = Alaska.$(p),
        s = v == 'f' ? 'fareFirst' : '',
        y = v == 'f' ? 'fareSelectedFirst' : '',
        c = Alaska.$(h).getElementsByClassName('fareSelected ' + y);
    for (e = 0; e < c.length; e++)
      c[e].id != o.id && (c[e].className = 'fare ' + s);
    for (o != null &&
             (o.className == 'fare ' + s ?
                  (o.className = 'fare ' + s + ' fareSelected ' + y, f = !0) :
                  (o.className = 'fare ' + s, f = !1)),
         t == 0 ? (Alaska.$('SelDepOptId').value = f ? i : '-1',
                  Alaska.$('SelDepFareCode').value = f ? n : '',
                  Alaska.$('DepartureOptionId').value = f ? i : '-1',
                  Alaska.$('DepartureFareCode').value = f ? n : '',
                  createCookie('DepOptId', Alaska.$('SelDepOptId').value, 1),
                  createCookie('DepFare', Alaska.$('SelDepFareCode').value, 1),
                  u == 1 && clearShowAllCookie(0)) :
                  t == 1 &&
                 (Alaska.$('SelRetOptId').value = f ? i : '-1',
                 Alaska.$('SelRetFareCode').value = f ? n : '',
                 Alaska.$('ReturnOptionId').value = f ? i : '-1',
                 Alaska.$('ReturnFareCode').value = f ? n : '',
                 createCookie('RetOptId', Alaska.$('SelRetOptId').value, 1),
                 createCookie('RetFare', Alaska.$('SelRetFareCode').value, 1),
                 u == 1 && clearShowAllCookie(1)),
         l = Alaska.$(h).getElementsByClassName('sliceoption'), e = 0;
         e < l.length; e++)
      l[e].style.display = f ? 'none' : 'block';
    Alaska.$(w).style.display = 'block';
    Alaska.$(b).style.display = f ? 'block' : 'none';
    f ? Alaska.$(a).setAttribute('disabled', 'disabled') :
        (Alaska.$(a).removeAttribute('disabled'), Alaska.CountFaresAndHide(t));
    t == 0 && scrollTo(0, Alaska.$(h).offsetTop)
  }
}
function createShopScrollCookie() {
  createCookie('VrtPos', scrollTop())
}
function createSearchCookie() {
  function r() {
    for (var t = document.getElementsByName('SearchFields.UpgradeOption'),
             n = 0, i = t.length;
         n < i; n++)
      if (t[n].checked) return t[n].value
  }
  var n = Alaska.$('srh-isow').checked ? 'o' : 'r', t, i;
  n += '|' + Alaska.$('geo-from').value;
  n += '|' + Alaska.$('geo-to').value;
  n += '|' + Alaska.$('departure-date').value;
  n += '|' + Alaska.$('return-date').value;
  n += '|' + Alaska.$('num-travelers').value;
  n += '|' + r();
  n += '|' + Alaska.$('srh-is-miles').checked;
  n += '|' + Alaska.$('discount-code').value;
  t = Alaska.$('is-cal');
  n += '|' + (t == null ? 'false' : t.checked);
  i = n.replace(/,/g, '~');
  createCookie('Search', encodeURIComponent(i), 1);
  Alaska.$('flights-form') ||
      (Alaska.$('cabin-coach').checked ?
           (createCookie('Cabin0', 'c'), createCookie('Cabin1', 'c')) :
           (createCookie('Cabin0', 'f'), createCookie('Cabin1', 'f')),
       createCookie('ShowFilter0', 0), createCookie('ShowFilter1', 0))
}
function clearShopScrollCookie() {
  createCookie('VrtPos', '0')
}
function clearSortByCookie() {
  createCookie('SortBy0', '1');
  createCookie('SortBy1', '1')
}
function clearShopDepCookie() {
  createCookie('DepOptId', '-1', 1);
  createCookie('DepFare', '', 1)
}
function clearShopRetCookie() {
  createCookie('RetOptId', '-1', 1);
  createCookie('RetFare', '', 1)
}
function clearShopAllCookie() {
  clearShopDepCookie();
  clearShopRetCookie();
  clearShopScrollCookie();
  clearSortByCookie();
  clearShowAllCookie(0);
  clearShowAllCookie(1)
}
function clearShowAllCookie(n) {
  n == 0 ? createCookie('ShowAllDep', '') : createCookie('ShowAllRet', '')
}
function getFareSelection() {
  var i = Alaska.$('back-form');
  currResultNum = i.elements.resultNum.value;
  currOptionId = i.elements.optionNum.value;
  var u = readCookie('Cabin' + currResultNum), f = u == 'f' ? 'fareFirst' : '',
      e = u == 'f' ? 'fareSelectedFirst' : '', n, t, r;
  switch (currResultNum) {
    case '0':
      n = readCookie('DepOptId');
      t = readCookie('DepFare');
      break;
    case '1':
      n = readCookie('RetOptId');
      t = readCookie('RetFare')
  }
  currOptionId == n &&
      (r = 'fare-' + currResultNum + '-' + n + '-' + t,
       Alaska.$(r) &&
           (Alaska.$(r).className = 'fare ' + f + ' fareSelected ' + e),
       i.elements.fareCode.value = t)
}
function showAllFlights(n) {
  for (var i = Alaska.$('result-' + n).getElementsByClassName('sliceoption'),
           t = 0;
       t < i.length; t++)
    i[t].style.display = 'block';
  Alaska.CountFaresAndHide(n);
  Alaska.$('showall' + n).style.display = 'none';
  createCookie('ShowAll' + (n == 0 ? 'Dep' : 'Ret'), '1')
}
function selectShoulderDate(n, t) {
  var r, i;
  Alaska.spinner.show();
  clearShopScrollCookie();
  var r = null, u = n.childNodes[1].value, f = Alaska.$('departure-date'),
      e = Alaska.$('searchType').value;
  e.toLowerCase() == 'roundtrip' && (r = Alaska.$('return-date'));
  t == 0 ?
      (Alaska.$('depShldrSel').value = !0, Alaska.$('retShldrSel').value = !1,
       f.value = u, clearShopDepCookie(), clearShowAllCookie(0)) :
      (Alaska.$('depShldrSel').value = !1, Alaska.$('retShldrSel').value = !0,
       r.value = u, clearShopRetCookie(), clearShowAllCookie(1));
  createShopScrollCookie();
  createSearchCookie();
  i = Alaska.$('searchForm');
  i.setAttribute('action', '/shopping/flightsshoulder');
  i.submit()
}
function scrollTop() {
  return filterResults(
      window.pageYOffset ? window.pageYOffset : 0,
      document.documentElement ? document.documentElement.scrollTop : 0,
      document.body ? document.body.scrollTop : 0)
}
function filterResults(n, t, i) {
  var r = n ? n : 0;
  return t && (!r || r > t) && (r = t), i && (!r || r > i) ? i : r
}
function goBack() {
  var n = Alaska.$('back-form');
  n.submit()
}
function submitToResult(n, t, i) {
  var r;
  if (i != -1) {
    r = Alaska.$('details-form');
    r.elements.resultNum.value = t;
    r.elements.fareCode.value = n;
    r.elements.optionNum.value = i;
    var o = 'fare-' + t + '-' + i + '-' + n, u = Alaska.$(o),
        f = readCookie('Cabin' + t), e = f == 'f' ? 'fareFirst' : '',
        s = f == 'f' ? 'fareSelectedFirst' : '';
    u.className == 'fare ' + e ?
        (u.className = 'fare fareSelected ' + s, anyFareSelected = !0,
         clearShowAllCookie(t)) :
        (u.className = 'fare' + e, anyFareSelected = !1);
    switch (t) {
      case 0:
        createCookie('DepOptId', i, 1);
        createCookie('DepFare', n, 1);
        createCookie('VrtPos', 180);
        break;
      case 1:
        createCookie('RetOptId', i, 1);
        createCookie('RetFare', n, 1)
    }
    r.submit()
  }
}
function fareruledetail(n, t, i, r) {
  var u = Alaska.$('farerule-form-' + n);
  u.categoryId.value = t;
  u.depAirportName.value = i;
  u.arrAirportName.value = r;
  u.submit()
}
function checkduplicate(n) {
  var i = readCookie('BookConfShown'), t = Alaska.$(n);
  IsDupBooked && IsDupSubmitted && i != 1 ?
      Alaska.modal.addStaticModalWithSubmit(
          t, 'Already booked?',
          'You may have purchased a similar flight on this device. Select OK to continue with this booking, or check your email to confirm recent purchases.',
          'OK', t.getAttribute('action')) :
      HasCubaDestination ?
      Alaska.modal.showCubaAdvisory(Alaska.$('cuba-info')) :
      t.submit();
  createCookie('BookConfShown', '0', 1)
}
function submitGoCheckoutForm() {
  Alaska.$('gocheckout-form').submit()
}
function clearTravelerForm() {
  Alaska.$('Traveler_FirstName').value = '';
  Alaska.$('Traveler_MiddleName').value = '';
  Alaska.$('Traveler_LastName').value = '';
  Alaska.$('Traveler_BirthDay').value = '';
  Alaska.$('Traveler_BirthMonth').value = '';
  Alaska.$('Traveler_BirthYear').value = '';
  Alaska.$('Loyalty_Code').value = 'AS';
  Alaska.$('Traveler_LoyaltyInfo_Number').value = '';
  Alaska.$('Traveler_LoyaltyInfo_Number').removeAttribute('readonly');
  Alaska.$('Traveler_KnownTravelerNumber').value = '';
  Alaska.$('Traveler_RedressNumber').value = '';
  Alaska.util.removeClass(Alaska.$('gender-male').parentNode, 'current');
  Alaska.util.removeClass(Alaska.$('gender-female').parentNode, 'current');
  Alaska.$('gender-male').checked = !1;
  Alaska.$('gender-female').checked = !1;
  Alaska.$('Traveler_DocumentNumber') &&
      (Alaska.$('Traveler_DocumentNumber').value = '');
  Alaska.$('Traveler_DocumentExpirationDate') &&
      (Alaska.$('Traveler_DocumentExpirationDate').value = '');
  Alaska.$('Traveler_Suffix').selectedIndex = 0;
  Alaska.$('CitizenDocType') && (Alaska.$('CitizenDocType').selectedIndex = 0);
  Alaska.$('Traveler_CountryOfResidence') &&
      (Alaska.$('Traveler_CountryOfResidence').selectedIndex = 0);
  Alaska.$('OtherDocTypeDiv') &&
      (Alaska.$('OtherDocTypeDiv').style.display = 'none')
}
function findDocTypeByCompanionId(n) {
  if (storedti)
    for (var t = 0; t < storedti.length; t++)
      if (storedti[t].Id == n) return storedti[t].DocumentType;
  return 'None'
}
function DiscountCodeDropCheck() {
  var n = Alaska.$('moreoptionsdiv');
  n &&
      (Alaska.$('discount-code').value == '' ?
           Alaska.util.removeClass(n, 'open') :
           Alaska.util.addClass(n, 'open'))
}
function TravelerDropCheck() {
  var n = Alaska.$('KTDiv');
  n &&
      (Alaska.$('Traveler_KnownTravelerNumber').value == '' &&
               Alaska.$('Traveler_RedressNumber').value == '' ?
           Alaska.util.removeClass(n, 'open') :
           Alaska.util.addClass(n, 'open'))
}
function ApisDropCheck() {
  if (Alaska.$('ApisDiv')) {
    var n = Alaska.$('ApisDiv'), i = Alaska.$('CitizenDocType'),
        t = Alaska.$('CitizenDocType').value;
    t == '' || t == 'None' ?
        (i.value = 'None', Alaska.util.removeClass(n, 'open')) :
        Alaska.util.addClass(n, 'open')
  }
}
function setReceiptEmail(n) {
  var t = Alaska.$('receiptemail');
  t.value = n.checked ? Alaska.$('traveler-contact-email').value : ''
}
function andrGetUserId() {
  if (typeof AppBooking != 'undefined') {
    var n = AppBooking.getUserId();
    n != '' && (Alaska.$('user-id').value = n)
  }
}
function andrAddCardAtConf(n, t) {
  typeof AppBooking != 'undefined' && AppBooking.addFlightCard(n, t)
}
Alaska.toggleSearch = function(n) {
  n.checked ?
      (Alaska.$('rt-container').style.display = 'none',
       Alaska.$('rt-error') && (Alaska.$('rt-error').style.display = 'none'),
       Alaska.$('return-date').value = '',
       Alaska.$('srh-type').value = 'OneWay') :
      (Alaska.$('rt-container').style.display = 'block',
       Alaska.$('rt-error') && (Alaska.$('rt-error').style.display = 'block'),
       Alaska.$('srh-type').value = 'RoundTrip')
};
Alaska.toggleMiles = function(n) {
  Alaska.$('geo-from').removeEventListener('keyup', Alaska.predictPartner);
  Alaska.$('geo-to').removeEventListener('keyup', Alaska.predictPartner);
  Alaska.$('geo-from').removeEventListener('keyup', Alaska.predictASPub);
  Alaska.$('geo-to').removeEventListener('keyup', Alaska.predictASPub);
  Alaska.$('geo-from-button').removeEventListener('click', Alaska.geoASPub);
  Alaska.$('geo-to-button').removeEventListener('click', Alaska.geoASPub);
  Alaska.$('geo-from-button').removeEventListener('click', Alaska.geoPartner);
  Alaska.$('geo-to-button').removeEventListener('click', Alaska.geoPartner);
  n.checked ?
      (Alaska.$('cabin-ftext').innerHTML = 'Business/First',
       Alaska.$('geo-to').addEventListener('keyup', Alaska.predictPartner),
       Alaska.$('geo-from').addEventListener('keyup', Alaska.predictPartner),
       Alaska.$('geo-from-button').addEventListener('click', Alaska.geoPartner),
       Alaska.$('geo-to-button').addEventListener('click', Alaska.geoPartner)) :
      (Alaska.$('cabin-ftext').innerHTML = 'First',
       Alaska.$('geo-to').addEventListener('keyup', Alaska.predictASPub),
       Alaska.$('geo-from').addEventListener('keyup', Alaska.predictASPub),
       Alaska.$('geo-from-button').addEventListener('click', Alaska.geoASPub),
       Alaska.$('geo-to-button').addEventListener('click', Alaska.geoASPub));
  Alaska.toggleUpgs();
  Alaska.toggleDiscountCode()
};
Alaska.toggleDiscountCodeRadio = function() {
  Alaska.$('rules-radio-btn').checked ?
      (Alaska.$('about-discount-code-container').style.display = 'block',
       Alaska.$('discount-code-terms-container').style.display = 'none') :
      (Alaska.$('about-discount-code-container').style.display = 'none',
       Alaska.$('discount-code-terms-container').style.display = 'block')
};
Alaska.toggleUpgs = function() {
  var t = document.querySelector('label[for=upg-miles]'),
      n = document.querySelector('.upg-options-container'),
      i = document.querySelector('label[for=upg-miles]');
  Alaska.$('cabin-first').checked ?
      (Alaska.$('upg-container').style.display = 'none',
       Alaska.$('upg-none').click()) :
      Alaska.$('srh-is-miles').checked ?
      (Alaska.$('upg-container').style.display = 'none',
       Alaska.$('upg-none').click()) :
      (Alaska.$('upg-container').style.display = 'block',
       t.style.display = 'block', Alaska.util.removeClass(n, 'four'),
       Alaska.util.addClass(n, 'five'))
};
Alaska.toggleDiscountCode = function() {
  Alaska.$('discount-code-container').style.display =
      Alaska.$('srh-is-miles').checked ? 'none' : 'block'
};
Alaska.toggleCal = function(n) {
  var t = Alaska.$('searchForm'), i = Alaska.$('use-miles-div'),
      r = Alaska.$('srh-is-miles'), f = Alaska.$('cabin-first'),
      u = Alaska.$('cabin-container');
  n != null &&
      (n.checked ? (r.checked && r.click(),
                    f.checked && Alaska.$('cabin-coach').click(),
                    i.style.display = 'none', u.style.display = 'none',
                    t.setAttribute('action', '/shopping/calendar')) :
                   (i.style.display = 'block', u.style.display = 'block',
                    t.setAttribute('action', '/shopping/flights')))
};
Alaska.UMNRMsg = function(n) {
  var t =
      'Unaccompanied minor service is required for each child ages 5 through 12 years old traveling without an adult and optional for children ages 13 through 17 years old. If your children are traveling alone, you will need to book your reservation on the ';
  t += n == 0 ?
      '<a href="badurl" onclick="Alaska.modal.remove();" target="_blank">full site<\/a>.' :
      'full site.';
  Alaska.modal.addStaticModal('Child traveling alone?', t)
};
Alaska.verifyDiscountCode = function() {
  Alaska.$('DiscountCode').value = Alaska.$('discount-code').value;
  var n = Alaska.$('searchForm');
  n.setAttribute('action', '/shopping/discountcode');
  Alaska.spinner.show();
  createSearchCookie();
  n.submit()
};
Alaska.CurrencyConverter = function() {
  var n = Alaska.$('currHtml'), t = getTotalFareAmount(),
      u = t == 0 ? '' : t.toString(), i = n.getElementsByClassName('amount')[0],
      r;
  i.setAttribute('value', u);
  Alaska.util.removeClass(i, 'input-validation-error');
  n.getElementsByClassName('form-error-msg')[0].style.display = 'none';
  n.getElementsByClassName('results')[0].style.display = 'none';
  t > 0 && CurrencyConversion(!1);
  r = n.innerHTML;
  Alaska.modal.addStaticModal('Currency converter', r)
};
Alaska.numTravelers = function(n) {
  var t = Alaska.$('num-travelers').value;
  n == 0 && t > 1 ? t-- : n == 1 && t < 7 && t++;
  Alaska.$('num-travelers').value = t;
  Alaska.$('tnum-display').innerHTML = t
};
Alaska.bagFeeMsg = function() {
  Alaska.modal.addStaticModal(
      'Baggage fees may apply',
      'If your itinerary is on Alaska Airlines flights, our baggage rules apply. See alaskaair.com/bagrules for details. For itineraries that include other airlines, their checked baggage rules and fees may apply.  Baggage rules and fees will be based on the itinerary chosen. The applicable first and second baggage fees will be displayed on the summary screen.')
};
Alaska.filterCabin = function(n, t, i) {
  var f, o, u, r, n, e;
  for (Alaska.spinner.show(),
       f = Alaska.$('result-' + t).getElementsByClassName('fare'), r = 0,
       o = f.length;
       r < o; r++)
    f[r].style.display = f[r].getAttribute('data-c') == n ? 'block' : 'none';
  if (createCookie('Cabin' + t, n),
      u = Alaska.$('result-' + t).getElementsByClassName('sliceoption'), i)
    for (r = 0; r < u.length; r++) u[r].style.display = 'block';
  if (Alaska.CountFaresAndHide(t),
      u[0].getElementsByClassName('fare').length == 5)
    for (r = 0; r < u.length; r++)
      n = readCookie('Cabin' + t), e = u[r].className,
      u[r].className = n == 'f' ? e.replace('fares3', 'fares2') :
                                  e.replace('fares2', 'fares3');
  setTimeout(function() {
    Alaska.spinner.hide()
  }, 150)
};
Alaska.filterCabinForDetails = function(n) {
  for (var t = document.getElementsByClassName('fare'),
           r = readCookie('Cabin' + n), i = 0, u = t.length;
       i < u; i++)
    t[i].style.display = t[i].getAttribute('data-c') == r ? 'block' : 'none';
  t.length == 5 &&
      (Alaska.$('details-form').className = r == 'c' ? 'fares3' : 'fares2')
};
Alaska.toggleFilters = function(n) {
  var i = Alaska.$('filter-bar' + n), t = Alaska.$('filter-cnt' + n);
  t.style.display == 'none' ?
      (i.className = 'filter-bar-open', t.style.display = 'block',
       createCookie('ShowFilter' + n, 1)) :
      (i.className = 'filter-bar', t.style.display = 'none',
       createCookie('ShowFilter' + n, 0))
};
Alaska.showLegend = function() {
  Alaska.modal.addStaticModal(
      Alaska.$('shopping-legend').firstElementChild.innerHTML,
      Alaska.$('shopping-legend').lastElementChild.innerHTML)
};
Alaska.CountFaresAndHide = function(n) {
  for (var t, r, f, i,
       e = Alaska.$('result-' + n).getElementsByClassName('sliceoption'),
       o = !1, s = readCookie('Cabin' + n), u = 0;
       u < e.length; u++) {
    t = e[u].getElementsByClassName('fare');
    switch (t.length) {
      case 4:
        r = 2;
        break;
      case 5:
        r = s == 'c' ? 3 : 2;
        break;
      case 6:
        r = 3
    }
    for (f = 0, i = 0; i < t.length; i++)
      if (t[i].getAttribute('data-c') == s &&
              t[i].getAttribute('data-a') != null && f++,
          f == r) {
        t[i].parentNode.style.display = 'none';
        o = !0;
        break
      }
  }
  Alaska.$('filter-msg' + n).innerHTML = o ?
      '<div class="server-msg-advisory">For additional flights and fares, change "Cabin" in filters. <\/div>' :
      ''
};
Alaska.toggleBreakdown = function() {
  var n = Alaska.$('breakdown-details'), t = Alaska.$('breakdown-head');
  n.style.display == 'none' || n.style.display == '' ?
      (n.style.display = 'block', t.className = 'breakdown-head-open') :
      (n.style.display = 'none', t.className = 'breakdown-head-close')
};
Alaska.updateTravelerInfos = function() {
  var n = Alaska.$('SelectedTravelerId'), i = Alaska.$('Loyalty_Code'),
      t = Alaska.$('Traveler_LoyaltyInfo_Number'),
      r = Alaska.$('CitizenDocType'), u = function() {
        if (n.value == '' || n.value == 'NEW')
          clearTravelerForm(), f(''), TravelerDropCheck();
        else
          for (var r = 0; r < storedti.length; r++)
            if (storedti[r].Id == n.value) {
              Alaska.$('Traveler_FirstName').value = storedti[r].FirstName;
              Alaska.$('Traveler_MiddleName').value = storedti[r].MiddleName;
              Alaska.$('Traveler_LastName').value = storedti[r].LastName;
              storedti[r].BirthDay == '1' && storedti[r].BirthMonth == '1' &&
                      storedti[r].BirthYear == '1' ?
                  (Alaska.$('Traveler_BirthDay').value = '',
                   Alaska.$('Traveler_BirthMonth').value = '',
                   Alaska.$('Traveler_BirthYear').value = '') :
                  (Alaska.$('Traveler_BirthDay').value = storedti[r].BirthDay,
                   Alaska.$('Traveler_BirthMonth').value =
                       storedti[r].BirthMonth,
                   Alaska.$('Traveler_BirthYear').value =
                       storedti[r].BirthYear);
              travelerIsAwardBooking ?
                  storedti[r].LoyaltyInfo != null &&
                          storedti[r].LoyaltyInfo.Program.Code == 'AS' ?
                  (t.value = storedti[r].LoyaltyInfo &&
                           storedti[r].LoyaltyInfo.Number ?
                       storedti[r].LoyaltyInfo.Number :
                       '',
                   t.value.length > 0 &&
                       t.setAttribute('readonly', 'readonly')) :
                  (t.value = '', t.removeAttribute('readonly')) :
                  (i.value = storedti[r].LoyaltyInfo &&
                           storedti[r].LoyaltyInfo.Program &&
                           storedti[r].LoyaltyInfo.Program.Code ?
                       storedti[r].LoyaltyInfo.Program.Code :
                       'AS',
                   t.value = storedti[r].LoyaltyInfo &&
                           storedti[r].LoyaltyInfo.Number ?
                       storedti[r].LoyaltyInfo.Number :
                       '');
              Alaska.$('Traveler_KnownTravelerNumber').value =
                  storedti[r].KnownTravelerNumber;
              Alaska.$('Traveler_RedressNumber').value =
                  storedti[r].RedressNumber;
              storedti[r].Gender === null || storedti[r].Gender == valUnknown ?
                  (Alaska.util.removeClass(
                       Alaska.$('gender-male').parentNode, 'current'),
                   Alaska.util.removeClass(
                       Alaska.$('gender-female').parentNode, 'current'),
                   Alaska.$('gender-male').checked = !1,
                   Alaska.$('gender-female').checked = !1) :
                  storedti[r].Gender == valMale ?
                  (Alaska.util.addClass(
                       Alaska.$('gender-male').parentNode, 'current'),
                   Alaska.util.removeClass(
                       Alaska.$('gender-female').parentNode, 'current'),
                   Alaska.$('gender-male').checked = !0,
                   Alaska.$('gender-female').checked = !1) :
                  (Alaska.util.addClass(
                       Alaska.$('gender-female').parentNode, 'current'),
                   Alaska.util.removeClass(
                       Alaska.$('gender-male').parentNode, 'current'),
                   Alaska.$('gender-male').checked = !1,
                   Alaska.$('gender-female').checked = !0);
              Alaska.$('CitizenDocType') &&
                  (Alaska.$('CitizenDocType').value =
                       storedti[r].Citizenship == 'Other' ? 'Other' :
                       storedti[r].Citizenship == ''      ? 'None' :
                                                       storedti[r].Citizenship +
                           '_' + storedti[r].DocumentType);
              Alaska.$('Traveler_DocumentNumber') &&
                  (Alaska.$('Traveler_DocumentNumber').value =
                       storedti[r].DocumentNumber);
              Alaska.$('Traveler_DocumentExpirationDate') &&
                  (Alaska.$('Traveler_DocumentExpirationDate').value =
                       storedti[r].DocumentExpirationDate);
              Alaska.$('Traveler_CountryOfResidence') &&
                  (Alaska.$('Traveler_CountryOfResidence').value =
                       storedti[r].CountryOfResidence);
              f(storedti[r].Citizenship);
              TravelerDropCheck();
              Alaska.$('Traveler_Suffix').value =
                  storedti[r].Suffix ? storedti[r].Suffix : 'None';
              break
            }
      }, e = function() {
        var r;
        if (t.value = '', n)
          if (n.value == 'myself') {
            for (r = 0; r < storedloyalties.length; r++)
              if (storedloyalties[r].Program.Code == i.value) {
                t.value =
                    storedloyalties[r].Number && storedloyalties[r].Number ?
                    storedloyalties[r].Number :
                    '';
                break
              }
          } else
            for (r = 0; r < storedti.length; r++)
              if (storedti[r].Id == n.value &&
                  storedti[r].LoyaltyInfo.Program.Code == i.value) {
                t.value =
                    storedti[r].LoyaltyInfo && storedti[r].LoyaltyInfo.Number ?
                    storedti[r].LoyaltyInfo.Number :
                    '';
                break
              }
      }, f = function() {
        ApisDropCheck();
        r && r.onchange && r.onchange()
      };
  travelerIsAwardBooking || Alaska.util.listenEvent(i, 'change', function() {
    e()
  });
  n ? (Alaska.util.listenEvent(
           n, 'change',
           function() {
             u()
           }),
       currentIndex > 0 && formIsValid == 'True' && formMode == 'ADD' ?
           (n.value = 'NEW', u()) :
           (travelerIsAwardBooking && t.value.length > 0 && n.value != 'NEW' &&
                storedti[n.selectedIndex].LoyaltyInfo != null &&
                t.setAttribute('readonly', 'readonly'),
            TravelerDropCheck(), ApisDropCheck())) :
      formMode == 'ADD' ?
      (clearTravelerForm(), formMode = '') :
      travelerIsSignedIn || (TravelerDropCheck(), ApisDropCheck())
};
Alaska.updateContactInfos = function() {
  var n = Alaska.$('SelectedTravelerId'), t = function() {
    var u, f, o, t, r, e, i;
    if (n)
      if (u = Alaska.$('EmailDropdown'), f = Alaska.$('PhoneNumberDropdown'),
          Alaska.$('Contact_ContactPhoneNumber_CountryCode').selectedIndex = 0,
          Alaska.$('Contact_ContactPhoneNumber_CountryIndex').value = 0,
          Alaska.$('phone-number').style.display = 'none',
          Alaska.$('email-address').style.display = 'none',
          Alaska.$('country-code').style.display = 'none',
          Alaska.$('phone-number-label').innerHTML = 'Phone (with area code)',
          Alaska.$('email-address-label').innerHTML = 'Email',
          Alaska.$('receiptemail-address-label').innerHTML =
              'Email confirm / receipt ',
          Alaska.$('Contact_ContactEmailAddress').value = '',
          Alaska.$('Contact_ContactPhoneNumber_Number').value = '',
          Alaska.util.removeClass(
              Alaska.$('Contact_ContactPhoneNumber_Number'),
              'input-validation-error'),
          Alaska.util.removeClass(
              Alaska.$('Contact_ContactEmailAddress'),
              'input-validation-error'),
          ClearDivErrors('email-address', 'form-error-msg'),
          ClearDivErrors('phone-number', 'form-error-msg'),
          hasDestContactPhoneError = 'False',
          document.getElementsByClassName('form-error-msg').length == 0 &&
              ClearErrors('server-msg-error'),
          n.value == 'NEW')
        Alaska.$('email-address-dropdown').style.display = 'none',
        Alaska.$('phone-number-dropdown').style.display = 'none',
        o = Alaska.$('country-code'), o.style.display = 'block',
        o.selectedIndex = 0, Alaska.$('email-address').style.display = 'block',
        Alaska.$('phone-number').style.display = 'block';
      else
        for (t = 0; t < storedti.length; t++)
          if (storedti[t].Id == n.value) {
            if (emptyList(u),
                storedti[t].EmailAddresses != null &&
                    storedti[t].EmailAddresses.length > 0) {
              for (Alaska.$('email-address-dropdown').style.display = 'block',
                  r = 0;
                   r < storedti[t].EmailAddresses.length; r++)
                i = document.createElement('option'),
                i.text = storedti[t].EmailAddresses[r].Address,
                i.value = storedti[t].EmailAddresses[r].Address,
                storedti[t].EmailAddresses[r].IsDefault == !0 &&
                    i.setAttribute('selected', !0),
                u.options.add(i);
              i = document.createElement('option');
              i.text = 'New email';
              i.value = 'NEW';
              u.options.add(i)
            } else
              Alaska.$('email-address-dropdown').style.display = 'none',
              Alaska.$('email-address').style.display = 'block',
              Alaska.$('Contact_ContactEmailAddress').value = '';
            if (emptyList(f),
                storedti[t].PhoneNumbers != null &&
                    storedti[t].PhoneNumbers.length > 0) {
              for (Alaska.$('phone-number-dropdown').style.display = 'block',
                  r = 0;
                   r < storedti[t].PhoneNumbers.length; r++)
                i = document.createElement('option'), e = '',
                storedti[t].PhoneNumbers[r].CountryCode != '1' &&
                    storedti[t].PhoneNumbers[r].Number.indexOf('+') == -1 &&
                    (e = '+' + storedti[t].PhoneNumbers[r].CountryCode + ' '),
                i.text = e + storedti[t].PhoneNumbers[r].Number,
                i.value = e + storedti[t].PhoneNumbers[r].Number,
                storedti[t].PhoneNumbers[r].IsDefault == !0 &&
                    i.setAttribute('selected', !0),
                f.options.add(i);
              i = document.createElement('option');
              i.text = 'New phone';
              i.value = 'NEW';
              f.options.add(i)
            } else
              Alaska.$('country-code').style.display = 'block',
              Alaska.$('phone-number-dropdown').style.display = 'none',
              Alaska.$('phone-number').style.display = 'block',
              Alaska.$('Contact_ContactPhoneNumber_Number').value = '';
            break
          }
  };
  n && Alaska.util.listenEvent(n, 'change', function(n) {
    n.preventDefault();
    t()
  })
};
Alaska.contactinfosetup = function() {
  var n = Alaska.$('SelectedTravelerId'), t = Alaska.$('PhoneNumberDropdown'),
      i = Alaska.$('EmailDropdown'), r = Alaska.$('ReceiptDropDown'),
      u = function() {
        var i = Alaska.$('country-code'), f = Alaska.$('phone-number-dropdown'),
            r = Alaska.$('phone-number'), u = Alaska.$('phone-number-label'), e;
        !n || n.value == 'NEW' || n.value == '' || t.length < 2 ?
            (i.style.display = r.style.display = 'block',
             f.style.display = 'none', u.innerHTML = 'Phone (with area code)') :
            (f.style.display = 'block',
             t.value == 'NEW' ?
                 (i.style.display = r.style.display = 'block',
                  u.innerHTML = 'New phone (with area code)',
                  e = Alaska.$('Contact_ContactPhoneNumber_Number'),
                  hasDestContactPhoneError == 'False' && e.value == '' &&
                      (Alaska.$('Contact_ContactPhoneNumber_CountryCode')
                           .selectedIndex = 0,
                       Alaska.$('Contact_ContactPhoneNumber_CountryIndex')
                           .value = 0)) :
                 hasDestContactPhoneError == 'True' ?
                 (t.value = 'NEW', i.style.display = r.style.display = 'block',
                  hasDestContactPhoneError = 'False') :
                 (i.style.display = r.style.display = 'none',
                  u.innerHTML = 'Phone (with area code)',
                  Alaska.$('Contact_ContactPhoneNumber_Number').value = ''))
      }, f = function() {
        var u = Alaska.$('email-address-dropdown'),
            t = Alaska.$('email-address'), r = Alaska.$('email-address-label');
        !n || n.value == 'NEW' || n.value == '' || i.length < 2 ?
            (t.style.display = 'block', u.style.display = 'none',
             r.innerHTML = 'Email') :
            (u.style.display = 'block',
             i.value == 'NEW' ?
                 (t.style.display = 'block', r.innerHTML = 'New email') :
                 (t.style.display = 'none', r.innerHTML = 'Email',
                  Alaska.$('Contact_ContactEmailAddress').value = ''))
      }, e = function() {
        var i = Alaska.$('receipt-email-address-dropdown'),
            n = Alaska.$('receipt-email-address'),
            t = Alaska.$('receiptemail-address-label');
        r.length < 2 ?
            (n.style.display = 'block', i.style.display = 'none',
             t.innerHTML = 'Email confirm / receipt') :
            (i.style.display = 'block',
             r.value == 'NEW' ? (n.style.display = 'block',
                                 t.innerHTML = 'New email confirm / receipt') :
                                (n.style.display = 'none',
                                 t.innerHTML = 'Email confirm / receipt',
                                 Alaska.$('receiptemail').value = ''))
      };
  t && (Alaska.util.listenEvent(t, 'change', function(n) {
    n.preventDefault();
    u()
  }), u());
  i && (Alaska.util.listenEvent(i, 'change', function(n) {
    n.preventDefault();
    f()
  }), f());
  r && (Alaska.util.listenEvent(r, 'change', function() {
    e()
  }), e());
  hasDestContactPhoneError = 'False'
};
Alaska.destinationinfosetup = function() {
  var e = Alaska.$('Contact_DestinationAddress_Street'),
      o = Alaska.$('Contact_DestinationAddress_Street2'),
      s = Alaska.$('Contact_DestinationAddress_City'),
      h = Alaska.$('Contact_DestinationAddress_ZipCode'),
      r = Alaska.$('Contact_DestinationDescription'),
      n = Alaska.$('Contact_DestinationCruiseLineName'),
      f = Alaska.$('Location_Name_Label'), t = Alaska.$('Location_Name_Row'),
      i = Alaska.$('Contact_DestinationLocationName'),
      u = Alaska.$('Other_Cruise_Label'), a = function() {
        e.setAttribute('placeholder', 'Required');
        o.setAttribute('placeholder', 'Optional');
        s.setAttribute('placeholder', 'Required');
        h.setAttribute('placeholder', 'Required')
      }, v = function() {
        e.setAttribute('placeholder', '');
        o.setAttribute('placeholder', '');
        s.setAttribute('placeholder', '');
        h.setAttribute('placeholder', '')
      }, c = function() {
        var s = Alaska.$('Address1_Row'), e = Alaska.$('Address1_Label'),
            o = Alaska.$('Address2_Row');
        t.style.display = 'none';
        i.style.display = 'block';
        s.style.display = 'block';
        o.style.display = 'none';
        e.innerHTML = 'Address';
        u.style.display = 'none';
        a();
        switch (r.value) {
          case 'None':
            e.innerHTML = 'Address line 1';
            o.style.display = 'block';
            v();
            break;
          case 'residential':
            e.innerHTML = 'Address line 1';
            o.style.display = 'block';
            break;
          case 'cruise':
            t.style.display = 'block';
            f.innerHTML = 'Cruise line';
            n.style.display = 'block';
            s.style.display = 'none';
            n.options[n.selectedIndex].value == 'Other' ?
                u.style.display = 'block' :
                i.style.display = 'none';
            break;
          case 'hotel':
            t.style.display = 'block';
            f.innerHTML = 'Hotel name';
            n.style.display = 'none';
            break;
          case 'business':
            t.style.display = 'block';
            f.innerHTML = 'Business name';
            n.style.display = 'none'
        }
      }, l = function() {
        r.value == 'cruise' &&
            (n.value == 'Other' ?
                 (t.style.display = 'block', i.style.display = 'block',
                  u.style.display = 'block') :
                 (i.style.display = 'none', i.value = '',
                  u.style.display = 'none'))
      };
  r && (Alaska.util.listenEvent(r, 'change', function(n) {
    n.preventDefault();
    c()
  }), c());
  n && (Alaska.util.listenEvent(n, 'change', function(n) {
    n.preventDefault();
    l()
  }), l())
};
Alaska.apisinfosetup = function() {
  if (Alaska.$('CitizenDocType')) {
    var n = Alaska.$('CitizenDocType'), u = Alaska.$('SelectedTravelerId'),
        t = function() {
          r()
        }, i = function() {
          Alaska.$('Traveler_DocumentNumber').value = '';
          Alaska.$('Traveler_DocumentExpirationDate').value = '';
          Alaska.$('Traveler_CountryOfResidence').value = 'None'
        }, r = function() {
          var t = Alaska.$('DocNumDiv'), i = Alaska.$('ExpDateDiv'),
              r = Alaska.$('CountryOfResidenceDiv'),
              u = Alaska.$('OtherDocTypeDiv'),
              f = Alaska.$('PermResDocTypeDiv'),
              e = Alaska.$('Traveler_DocumentNumber'),
              o = Alaska.$('Traveler_DocumentExpirationDate'),
              s = Alaska.$('Traveler_CountryOfResidence');
          switch (n.value) {
            case 'None':
              t.style.display = 'none';
              i.style.display = 'none';
              r.style.display = 'none';
              u.style.display = 'none';
              f.style.display = 'none';
              break;
            case 'US_Passport':
            case 'MX_Passport':
            case 'CA_Passport':
              t.style.display = 'block';
              i.style.display = 'block';
              r.style.display = 'block';
              u.style.display = 'none';
              f.style.display = 'none';
              break;
            case 'CA_PermanentResident':
            case 'MX_PermanentResident':
              t.style.display = 'none';
              i.style.display = 'none';
              r.style.display = 'none';
              u.style.display = 'none';
              f.style.display = 'block';
              break;
            case 'US_Other':
            case 'CA_Other':
            case 'MX_Other':
            case 'Other':
              t.style.display = 'none';
              i.style.display = 'none';
              r.style.display = 'none';
              u.style.display = 'block';
              f.style.display = 'none'
          }
        };
    n && (n.onchange = t, Alaska.util.listenEvent(n, 'change', function(n) {
      n.preventDefault();
      i();
      t()
    }), t())
  }
};
Alaska.bookingConfirmation = function() {
  createCookie('BookConfShown', '1', 1)
};
