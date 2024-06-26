function getXHR() {
  if (window.XMLHttpRequest) return req = new XMLHttpRequest, !0;
  try {
    return req = new ActiveXObject('Msxml2.XMLHTTP'), !0
  } catch (n) {
    try {
      return req = new ActiveXObject('Microsoft.XMLHTTP'), !0
    } catch (n) {
      return req = !1, !1
    }
  }
}
function CollapseSignIn() {
  for (var i, t = Alaska.util.getElementsByClassName('drop-head'), n = 0;
       n < t.length; n++)
    i = function() {
      var u = t[n], i = u.parentNode, r;
      Alaska.util.hasClass(i, 'u-sign-in') &&
          (r = Alaska.$('main'),
           Alaska.util.hasClass(i, 'open') &&
               (Alaska.util.removeClass(i, 'open'),
                Alaska.util.removeClass(r, 'sign-in-open')))
    }(n);
  return !0
}
function AddCookies(n, t, i) {
  var r = new Date;
  return document.cookie = 'AuthToken=' + n.at + ';path=/;secure',
         document.cookie = 'DisplayName=' + n.dn + ';path=/;secure',
         r.setDate(r.getDate() + 30),
         i ? (document.cookie =
                  'RememberMe=True;expires=' + r + ';path=/;secure',
              document.cookie =
                  'UserID=' + t + ';expires=' + r + ';path=/;secure') :
             (document.cookie = 'RememberMe=False;path=/;secure',
              document.cookie = 'UserID=' + t + ';path=/;secure'),
         !0
}
function ShowFailedSignInMessage(n) {
  Alaska.util.showClientMsg(n);
  Alaska.util.addClass(Alaska.$('signin-name'), 'input-validation-error');
  Alaska.util.addClass(Alaska.$('signin-password'), 'input-validation-error');
  scrollTo(0, 0)
}
function confirmScheduleChange(n, t, i) {
  if (getXHR()) {
    var r = 'lastName=' + n + '&reservationIdentifier=' + t;
    req.open('POST', '/ScheduleChange/Confirm?' + r, !0);
    req.onreadystatechange = function() {
      req.readyState === 4 &&
          (req.status === 200 ?
               i.call({}, !0) :
               (Alaska.$('client-msg-div').textContent =
                    'We\'re sorry - there was a problem communicating with Alaska Airlines. Please try again or call Reservations at your convenience to confirm your trip details.',
                i.call({}, !1)))
    }
  }
  req.send()
}
function SignIn(n, t, i, r, u) {
  HideFailedSignInMsg();
  Alaska.$(r).disabled = !0;
  var f = encodeURIComponent(Alaska.$(n).value),
      e = encodeURIComponent(Alaska.$(t).value), o = Alaska.$(i).checked,
      s = 'userid=' + f + '&password=' + e;
  getXHR() &&
      (req.open('POST', '/account/logonasync', !0),
       req.setRequestHeader(
           'Content-type', 'application/x-www-form-urlencoded'),
       req.onreadystatechange = function() {
         var n, i;
         req.readyState == 4 &&
             (Alaska.$(r).disabled = !1,
              req.status == 200 &&
                  (n = JSON.parse(req.responseText),
                   n.s == '1' ?
                       (s_gi && n.ou &&
                            (i = s_gi(n.ou), i.linkTrackVars = 'events',
                             i.linkTrackEvents = 'event7', i.events = 'event7',
                             i.eVar5 = n.t, i.eVar6 = n.mp, i.t(),
                             i.events = ''),
                        AddCookies(n, f, o),
                        u == 'False' ? ShowSignOut(n.dn) :
                                       window.location.reload()) :
                       ShowFailedSignInMessage(n.msg),
                   Alaska.$(t).value = ''))
       }, req.send(s))
}
function SignOut(n) {
  document.cookie = 'AuthToken=;path=/';
  document.cookie = 'DisplayName=;path=/';
  readCookie('RememberMe') === 'False' && (document.cookie = 'UserID=;path=/');
  n == 'False' ? (Alaska.$('_SignOut').style.display = 'none',
                  Alaska.$('_SignOutSubmit').value = 'Sign out ',
                  ShowSignIn('_SignInSubmit')) :
                 window.location.reload()
}
function HideFailedSignInMsg() {
  var n = Alaska.$('client-msg-div');
  n.removeAttribute('class');
  n.innerHTML = ''
}
function ShowSignIn(n) {
  var r = Alaska.$('_SignInWrapper'), t, i;
  r &&
      (r.style.display = 'block',
       Alaska.$(n) &&
           (Alaska.$(n).value = 'Sign In', Alaska.$(n).disabled = !1,
            t = readCookie('RememberMe'),
            t != null &&
                (t == 'True' ?
                     (Alaska.$('signin-remember').checked = !0,
                      i = readCookie('UserID'),
                      i != null &&
                          (Alaska.$('signin-name').value = unescape(i))) :
                     (Alaska.$('signin-remember').checked = !1,
                      Alaska.$('signin-name').value = ''))))
}
function ShowSignOut(n) {
  var t = Alaska.$('_SignInWrapper'), i;
  t &&
      (i = CollapseSignIn(), t.style.display = 'none',
       Alaska.$('_SignOut').style.display = 'block', null == n && (n = ''),
       Alaska.$('_SignOutSubmit').innerHTML = 'Sign out  ' + n);
  HideFailedSignInMsg()
}
function ShowProperAccordion() {
  var n = '', t;
  typeof sessionExpired != 'undefined' && sessionExpired != 'True' &&
      (n = readCookie('AuthToken'));
  n != null && n != '' ? (t = readCookie('DisplayName'), ShowSignOut(t)) :
                         ShowSignIn('_SignInSubmit')
}
function readCookie(n) {
  for (var t, r = n + '=', u = document.cookie.split(';'), i = 0; i < u.length;
       i++) {
    for (t = u[i]; t.charAt(0) == ' ';) t = t.substring(1, t.length);
    if (t.indexOf(r) == 0) return t.substring(r.length, t.length)
  }
  return null
}
function ToggleAllRadio() {
  var u = Alaska.util.getElementsByClassName('radio-controller', 'div'), r, n,
      t, i;
  if (u)
    for (r = 0; r < u.length; r++)
      if (n = u[r].getElementsByTagName('input'), n)
        for (t = 0; t < n.length; t++)
          if (n[t] && n[t].checked) {
            i = n[t].parentNode;
            i && (i.click ? i.click() : i.onclick && i.onclick());
            break
          }
}
function createCookie(n, t, i) {
  var u, r;
  i ? (r = new Date, r.setTime(r.getTime() + i * 864e5),
       u = '; expires=' + r.toGMTString()) :
      u = '';
  document.cookie = n + '=' + t + u + '; path=/;secure'
}
function eraseCookie(n) {
  createCookie(n, '', -1)
}
function areCookiesEnabled() { /*SURROGATE*/
  return true;
}
function GetPriorityList(n) {
  Alaska.spinner.show();
  var t = Alaska.$('prioritylist-form');
  t.setAttribute('action', n);
  t.submit()
}
function submitForm(n) {
  var t = document.forms[0];
  t.setAttribute('action', n);
  t.submit(t)
}
function GetLocalDateTime() {
  var i = ' am', t = new Date, f = t.getDate(), e = t.getMonth() + 1,
      o = t.getFullYear().toString(), n = t.getHours(), r = t.getMinutes(), u;
  n == 0      ? (n = 12, i = ' am') :
      n == 12 ? i = ' pm' :
                n > 12 && (n = n - 12, i = ' pm');
  r < 10 && (r = '0' + r);
  u = Alaska.$('lastupdated');
  u != null &&
      (u.innerHTML = 'Last updated: ' + n + ':' + r + ' ' + i + ', ' + e + '/' +
           f + '/' + o.substr(2, 2))
}
function emptyList(n) {
  if (n != null)
    while (n.options.length) n.options[0] = null
}
function toggleHaveMPNumber() {
  var r = Alaska.$('HaveMPNumber'), n = Alaska.$('haveMPDiv'),
      t = Alaska.$('mpDiv'), i = Alaska.$('mailingAddrDiv');
  r.checked ? (t.style.display = 'block', i.style.display = 'none',
               Alaska.util.removeClass(n, 'last')) :
              (t.style.display = 'none', i.style.display = 'block',
               Alaska.util.addClass(n, 'last'))
}
function numberWithCommas(n) {
  return n.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',')
}
function trackFullSiteLink() {
  if (s_gi) {
    var n = s_gi(s_account);
    n.linkTrackVars = 'events';
    n.linkTrackEvents = 'event19';
    n.events = 'event19';
    n.tl(this, 'o', 'Footer : Full Site');
    n.events = ''
  }
}
function currencyFormat(n) {
  return '$' + n.toFixed(2).replace(/(\d)(?=(\d{3})+(?!\d))/g, '$1,')
}
String.prototype.trim || (String.prototype.trim = function() {
  return this.replace(/^\s+|\s+$/g, '')
});
var Alaska = {};
Alaska.$ = function(n) {
  return document.getElementById(n)
};
Alaska.setup = function() {
  if (navigator.userAgent.match(/iPhone/i) ||
      navigator.userAgent.match(/iPad/i)) {
    var n = document.querySelector('meta[name="viewport"]');
    n &&
        (n.content = 'width=device-width, minimum-scale=1.0, maximum-scale=1.0',
         document.body.addEventListener('gesturestart', function() {
           n.content =
               'width=device-width, minimum-scale=0.25, maximum-scale=1.6'
         }, !1))
  }
  !Alaska.$('flights-form') &&
      (!location.hash ||
       location.hash &&
           Alaska.util.getElementsByClassName('boarding-pass')[0]) &&
      setTimeout(function() {
        window.scrollTo(0, 1);
        setTimeout(function() {
          window.scrollTo(0, 0)
        }, 0)
      }, 0)
};
Alaska.drop = function() {
  for (var i, t = Alaska.util.getElementsByClassName('drop-head'), n = 0;
       n < t.length; n++)
    i = function(n) {
      var r = t[n], i = r.parentNode;
      Alaska.util.listenEvent(r, 'click', function() {
        if (Alaska.util.hasClass(i, 'u-sign-in')) {
          var n = Alaska.$('main');
          Alaska.util.hasClass(i, 'open') ?
              (Alaska.util.removeClass(i, 'open'),
               Alaska.util.removeClass(n, 'sign-in-open')) :
              (areCookiesEnabled() || ShowFailedSignInMessage(enableCookiesMsg),
               Alaska.util.addClass(i, 'open'),
               Alaska.util.addClass(n, 'sign-in-open'))
        } else
          Alaska.util.hasClass(i, 'open') ? Alaska.util.removeClass(i, 'open') :
                                            Alaska.util.addClass(i, 'open')
      })
    }(n)
};
Alaska.persistentDrop = function() {
  var t = Alaska.$('bp-drop'), n = Alaska.$('bp-drop-content');
  Alaska.util.listenEvent(t, 'click', function() {
    Alaska.util.hasClass(n, 'open') ? Alaska.util.removeClass(n, 'open') :
                                      Alaska.util.addClass(n, 'open')
  })
};
Alaska.toggleRadio = function(n) {
  var i, s, f, r, u, t, e, o;
  if (n.className.match(/\bcurrent\b/) === null) {
    for (i = n.parentNode.getElementsByTagName('label'), t = 0; t < i.length;
         t++)
      Alaska.util.removeClass(i[t], 'current');
    if (Alaska.util.addClass(n, 'current'), s = n.childNodes[0].value,
        n.childNodes[0].className.match(/select[^\s]+/g)) {
      for (f = Alaska.util.getParentByTagName(n, 'fieldset'),
          r = Alaska.util.getElementsByClassName('toggle', 'div', f), t = 0;
           t < r.length; t++)
        r[t].style.display = 'none';
      for (u = n.childNodes[0].className.split(' '), t = 0; t < u.length; t++)
        e = u[t].match(/select[^\s]+/g).toString(), o = Alaska.$(e),
        o.style.display = 'block'
    }
  } else
    return !1
};
Alaska.toggleRadioList = function(n) {
  n.childNodes[1].setAttribute('checked', 'checked');
  Alaska.toggleRadio(n)
};
Alaska.modal = {
  init: function(n, t, i, r, u, f, e) {
    for (var s = Alaska.util.getElementsByClassName(n), o = 0, h = s.length;
         o < h; o += 1)
      Alaska.util.listenEvent(s[o], 'click', function(n) {
        if (n.preventDefault(), e)
          Alaska.modal.addLinkModal(e, t, i, r, u);
        else {
          var o = Alaska.util.getParentByTagName(n.target, 'form');
          Alaska.modal.add(o, t, i, r, u, f)
        }
      })
  },
  addStaticModalFoodDetail: function(n, t, i, r) {
    var u = document.createElement('div'), f = document.createElement('div'),
        e = Alaska.util.getDocumentHeight();
    u.setAttribute('class', 'disable-ui');
    u.setAttribute('id', 'modal-background');
    u.setAttribute('style', 'height: ' + e + 'px;');
    f.setAttribute('id', 'modal-window');
    f.innerHTML = '<img src="' + n + '" alt="' + t +
        '" style="width:268px;height:189px;margin:0 auto; display:block;"><\/img><div class="b intro" style="font-size:16px;padding-top:10px;">' +
        t + '<\/div><div><div style="font-size:12px">' + i +
        '<\/div><div style="padding-top:10px;font-weight:bold;">' + r +
        '<\/div><\/div><div><input type="button" class="button" id="dialog-cancel" value="Close"><\/div>';
    u.appendChild(f);
    document.body.appendChild(u);
    f.setAttribute('style', 'top: ' + Alaska.modal.calculateTop(f) + ';');
    Alaska.modal.addLinkHandlers()
  },
  convertToModal: function(n) {
    var i = Alaska.util.getDocumentHeight(), t;
    n.setAttribute('class', 'disable-ui');
    n.setAttribute('style', 'height: ' + i + 'px;');
    t = n.firstElementChild;
    t.setAttribute('style', 'top: ' + Alaska.modal.calculateTop(t) + ';');
    Alaska.util.listenEvent(Alaska.$('dialog-cancel'), 'click', function() {
      n.style.display = 'none'
    })
  },
  addStaticModal: function(n, t) {
    var r = document.createElement('div'), i = document.createElement('div'),
        u = Alaska.util.getDocumentHeight();
    r.setAttribute('class', 'disable-ui');
    r.setAttribute('id', 'modal-background');
    r.setAttribute('style', 'height: ' + u + 'px;');
    i.setAttribute('id', 'modal-window');
    n != null && (i.innerHTML = '<h2 style="font-weight:bold">' + n + '<\/h2>');
    i.innerHTML += t +
        '<div class="form-row last"><input type="button" class="button" id="dialog-cancel" value="Close"><\/div>';
    r.appendChild(i);
    document.body.appendChild(r);
    i.setAttribute('style', 'top: ' + Alaska.modal.calculateTop(i) + ';');
    Alaska.modal.addLinkHandlers()
  },
  addStaticModalWithSubmit: function(n, t, i, r, u) {
    var f = document.createElement('div'), e = document.createElement('div'),
        o = Alaska.util.getDocumentHeight();
    f.setAttribute('class', 'disable-ui');
    f.setAttribute('id', 'modal-background');
    f.setAttribute('style', 'height: ' + o + 'px;');
    e.setAttribute('id', 'modal-window');
    e.innerHTML = '<h2 style="font-weight:bold">' + t + '<\/h2>' + i +
        '<div class="form-row last"><input type="button" class="button" id="dialog-submit" value="' +
        r + '"><\/div>';
    n.setAttribute('action', u);
    f.appendChild(e);
    document.body.appendChild(f);
    e.setAttribute('style', 'top: ' + Alaska.modal.calculateTop(e) + ';');
    Alaska.modal.addDialogHandlers(n)
  },
  addLinkModal: function(n, t, i, r, u) {
    var f = document.createElement('div'), e = document.createElement('div'),
        o = Alaska.util.getDocumentHeight();
    f.setAttribute('class', 'disable-ui');
    f.setAttribute('id', 'modal-background');
    f.setAttribute('style', 'height: ' + o + 'px;');
    e.setAttribute('id', 'modal-window');
    e.innerHTML = '<h2 style="font-weight:bold">' + t + '<\/h2>' + i +
        '<div class="form-row last"><a class="button-link secondary" id="dialog-cancel">' +
        r + '<\/a><a href="' + n + '" class="button-link" id="dialog-submit">' +
        u + '<\/a><\/div>';
    f.appendChild(e);
    document.body.appendChild(f);
    e.setAttribute('style', 'top: ' + Alaska.modal.calculateTop(e) + ';');
    Alaska.modal.addLinkHandlers()
  },
  addRedirectModal: function(n, t, i) {
    var r = document.createElement('div'), u = document.createElement('div'),
        f = Alaska.util.getDocumentHeight();
    r.setAttribute('class', 'disable-ui');
    r.setAttribute('id', 'modal-background');
    r.setAttribute('style', 'height: ' + f + 'px;');
    u.setAttribute('id', 'modal-window');
    u.innerHTML = '<h2 style="font-weight:bold">' + t + '<\/h2>' + i +
        '<div class="form-row last"><a href="' + n +
        '" class="button-link" style="width:100%" id="dialog-redirect">Close<\/a><\/div>';
    r.appendChild(u);
    document.body.appendChild(r);
    u.setAttribute('style', 'top: ' + Alaska.modal.calculateTop(u) + ';');
    Alaska.modal.addRedirectHandlers()
  },
  add: function(n, t, i, r, u, f) {
    var e = document.createElement('div'), o = document.createElement('div'),
        s = Alaska.util.getDocumentHeight();
    e.setAttribute('class', 'disable-ui');
    e.setAttribute('id', 'modal-background');
    e.setAttribute('style', 'height: ' + s + 'px;');
    o.setAttribute('id', 'modal-window');
    o.innerHTML = '<h2 style="font-weight:bold">' + t + '<\/h2>' + i +
        '<div class="form-row last"><input type="button" class="button secondary" id="dialog-cancel" value="' +
        r + '"><input type="submit" class="button" id="dialog-submit" value="' +
        u + '"><\/div>';
    n.setAttribute('action', f);
    e.appendChild(o);
    document.body.appendChild(e);
    o.setAttribute('style', 'top: ' + Alaska.modal.calculateTop(o) + ';');
    Alaska.modal.addDialogHandlers(n)
  },
  show: function(n) {
    var t = document.createElement('div'), i = document.createElement('div'),
        u = Alaska.util.getDocumentHeight(), r = document.createElement('div');
    r.appendChild(n.cloneNode(!0));
    t.setAttribute('class', 'disable-ui');
    t.setAttribute('id', 'modal-background');
    t.setAttribute('style', 'height: ' + u + 'px;');
    i.setAttribute('id', 'modal-window');
    i.innerHTML = r.innerHTML;
    t.appendChild(i);
    document.body.insertBefore(t, document.body.childNodes[0]);
    i.setAttribute('style', 'top: ' + Alaska.modal.calculateTop(i) + ';')
  },
  showSeatUpgrade: function(n, t, i) {
    var u = document.createElement('div'), r = document.createElement('div'),
        o = Alaska.util.getDocumentHeight(), f = document.createElement('div'),
        e;
    f.appendChild(n.cloneNode(!0));
    u.setAttribute('class', 'disable-ui');
    u.setAttribute('id', 'modal-background');
    u.setAttribute('style', 'height: ' + o + 'px;');
    r.setAttribute('id', 'modal-window-no-padding');
    r.innerHTML = f.innerHTML;
    u.appendChild(r);
    document.body.insertBefore(u, document.body.childNodes[0]);
    r.setAttribute('style', 'top: ' + Alaska.modal.calculateTop(r) + ';');
    e = r.querySelector('button');
    Alaska.util.listenEvent(e, 'click', function() {
      Alaska.modal.remove();
      var n = i ? 'Checkin' : 'Seats', r = n + ':UpgradetoPremiumClass:Close';
      t || (r = n + ':UpgradetoPreferredPlus:Close');
      Alaska.omniture.reportClick(r)
    })
  },
  showCubaAdvisory: function(n) {
    var i = document.createElement('div'), t = document.createElement('div'),
        c = Alaska.util.getDocumentHeight(), f = document.createElement('div'),
        r, h, u;
    f.appendChild(n.cloneNode(!0));
    i.setAttribute('class', 'disable-ui');
    i.setAttribute('id', 'modal-background');
    i.setAttribute('style', 'height: ' + c + 'px;');
    t.setAttribute('id', 'modal-window');
    t.setAttribute('class', 'scrollable');
    t.innerHTML = f.innerHTML;
    i.appendChild(t);
    document.body.appendChild(i);
    var e = window.innerHeight * .84, o = t.querySelectorAll('button'), s = 0;
    for (r = 0; r < o.length; r++) s += o[r].offsetHeight;
    h = t.querySelector('#cuba-info .scrollable');
    h.style.maxHeight = e - s + 'px';
    u = 'top: ' + Alaska.modal.calculateTop(t) + ';';
    u += 'max-height: ' + e + 'px;';
    t.setAttribute('style', u)
  },
  remove: function() {
    window.removeEventListener('resize', Alaska.modal.reCalc);
    document.body.removeChild(Alaska.$('modal-background'))
  },
  calculateTop: function(n) {
    var r = document.documentElement.scrollTop ?
        document.documentElement.scrollTop :
        document.body.scrollTop,
        u = window.innerHeight, t = u / 2 + r, i = 0;
    return i = n ? t - n.clientHeight / 2 : t - 75, i + 'px'
  },
  calculateLeft: function() {
    var n = window.innerWidth / 2 - 144;
    return n + 'px'
  },
  reCalc: function() {
    Alaska.$('modal-window')
        .setAttribute(
            'style',
            'top: ' + Alaska.modal.calculateTop(Alaska.$('modal-window')) +
                '; left: ' + Alaska.modal.calculateLeft())
  },
  addDialogHandlers: function(n) {
    var t = Alaska.$('dialog-cancel'), i = Alaska.$('dialog-submit');
    t && Alaska.util.listenEvent(t, 'click', function() {
      Alaska.modal.remove()
    });
    i && Alaska.util.listenEvent(i, 'click', function() {
      n.submit()
    })
  },
  addRedirectHandlers: function() {
    var n = Alaska.$('dialog-redirect');
    Alaska.util.listenEvent(n, 'click', function() {
      window.location = n.getAttribute('href')
    })
  },
  addLinkHandlers: function() {
    Alaska.util.listenEvent(Alaska.$('dialog-cancel'), 'click', function() {
      Alaska.modal.remove()
    })
  }
};
Alaska.omniture = {
  reportClick: function(n) {
    if (s_gi) {
      var t = s_gi(s_account);
      t.linkTrackVars = 'prop3';
      t.linkTrackEvents = 'None';
      t.prop3 = n;
      t.tl(!0, 'o', n);
      t.prop3 = ''
    }
  }
};
Alaska.spinner = {
  show: function(n) {
    if ((n ||
         !Alaska.util.userAgentContain('Android 2.') &&
             !Alaska.util.userAgentContain('ALKApp')) &&
        (aSpinner = Alaska.$('aSpinner'), aSpinner)) {
      aSpinner.style.top = Alaska.spinner.calcTop(46);
      aSpinner.style.left = Alaska.spinner.calcLeft(44);
      var t = Alaska.$('spinner-cnt');
      t.style.height = Alaska.util.getDocumentHeight() + 'px';
      t.style.display = 'block'
    }
  },
  calcTop: function(n) {
    var t = document.documentElement.scrollTop ?
        document.documentElement.scrollTop :
        document.body.scrollTop,
        i = window.innerHeight / 2 + t, r = i - n / 2;
    return r + 'px'
  },
  calcLeft: function(n) {
    var t = window.innerWidth / 2 - n / 2;
    return t + 'px'
  },
  hide: function() {
    var n = Alaska.$('spinner-cnt');
    n && (n.style.display = 'none')
  }
};
Alaska.cityPairDoesntDoYesterday = function() {
  var n = Alaska.$('geo-from'), t = Alaska.$('geo-to'), i = function() {
    var n = Alaska.$('yesterday'), t = Alaska.$('today');
    n.checked &&
        (n.setAttribute('checked', 'unchecked'),
         Alaska.util.removeClass(n.parentNode, 'current'),
         t.setAttribute('checked', 'checked'),
         Alaska.util.addClass(t.parentNode, 'current'))
  };
  n && Alaska.util.listenEvent(n, 'focus', i);
  t && Alaska.util.listenEvent(t, 'focus', i)
};
Alaska.calculateBagFees = function() {
  var i = Alaska.util.getElementsByClassName('bag-fee'), n, t, o, u, s, f, e;
  if (i.length > 0) {
    var h = Alaska.$('bag-fee-form'), c = Alaska.$('bag-fee-continue'), r = 0;
    for (n = 0; n < i.length; n++)
      t = i[n],
      t &&
          (o = t.options[t.selectedIndex].text, u = o.split('$'),
           u.length > 1 && (r += parseFloat(u[1])));
    s = document.createTextNode('$' + r.toFixed(2));
    f = Alaska.$('bag-fees-total');
    f.replaceChild(s, f.childNodes[0]);
    e = Alaska.$('bag-fees-require-pay-at-airport');
    e && (e.style.display = r > 0 ? 'block' : 'none')
  }
};
Alaska.initBagFees = function() {
  for (var i, t = Alaska.util.getElementsByClassName('bag-fee'), n = 0;
       n < t.length; n++)
    i = function() {
      var i = t[n];
      i && Alaska.util.listenEvent(i, 'change', Alaska.calculateBagFees)
    }(n)
};
Alaska.clearTxt = function(n) {
  var t = n.parentNode.getElementsByTagName('input')[0];
  t.value = '';
  t.focus()
};
Alaska.buildInputSelections = function(n, t, i) {
  var f = document.createElement('ol'), e = Alaska.$(t),
      c = e.parentNode.parentNode, r, o, y;
  for (f.setAttribute('class', 'input-selections'),
       f.setAttribute('id', 'input-selections-' + t), r = 0;
       r < n.length; r++) {
    var l = n[r], u = document.createElement('li'),
        a = document.createTextNode(l);
    u.appendChild(a);
    u.setAttribute('data-value', n[r]);
    u.setAttribute('class', 'input-selection');
    r == n.length - 1 && u.setAttribute('class', 'last');
    f.appendChild(u)
  }
  Alaska.util.addClass(e, 'geo-active');
  c.appendChild(f);
  var s = Alaska.$('input-selections-' + t), h = s.getElementsByTagName('li'),
      v = function(n) {
        (n.target !== Alaska.$('input-selections-' + t) ||
         Alaska.util.hasClass(n.target, 'input-selection')) &&
            (n.stopPropagation(), Alaska.removeInputSelections(t))
      };
  for (Alaska.util.listenEvent(document.body, 'click', v), o = 0; o < h.length;
       o++)
    y = function(n) {
      var t = h[n];
      Alaska.util.listenEvent(t, 'click', function() {
        var n = t.getAttribute('data-value');
        e.value = n;
        s.parentNode.removeChild(s);
        Alaska.util.removeClass(e, 'geo-active');
        typeof i != 'undefined' && i(n)
      })
    }(o)
};
Alaska.updateInputSelections = function(n, t) {
  var h = Alaska.$('input-selections-' + t), r = h.getElementsByTagName('li'),
      u, f, o, i, e, s;
  if (r.length != n.length && n.length - r.length > 0)
    for (u = r.length - 1; u < n.length; u++)
      f = document.createElement('li'), o = document.createTextNode(n[u]),
      f.appendChild(o), f.setAttribute('data-value', n[u]),
      f.setAttribute('class', 'input-selection'),
      u == n.length - 1 && f.setAttribute('class', 'last'),
      r[u].parentNode.appendChild(f);
  for (i = 0; i < n.length; i++)
    e = n[i], r[i].innerHTML = e, r[i].setAttribute('data-value', e),
    Alaska.util.hasClass(r[i], 'last') && Alaska.util.removeClass(r[i], 'last'),
    i == n.length - 1 && Alaska.util.addClass(r[i], 'last');
  for (s = r.length, i = s - 1; i >= n.length; i--)
    r[i].parentNode.removeChild(r[i])
};
Alaska.removeInputSelections = function(n) {
  if (Alaska.$('input-selections-' + n)) {
    var i = Alaska.$(n), t = Alaska.$('input-selections-' + n),
        r = t.parentNode;
    r.removeChild(t);
    Alaska.util.removeClass(i, 'geo-active')
  }
};
Alaska.predictPartner = function() {
  Alaska.predict(this.id, 'Partners')
};
Alaska.predictASPub = function() {
  Alaska.predict(this.id, 'ASPublished')
};
Alaska.predictCheckin = function() {
  Alaska.predict(this.id, 'Checkin')
};
Alaska.predictVars = {
  curTime: 0,
  delayTime: 0 /* SURROGATE: USED TO BE 300 */,
  predictCalled: !1,
  lastCalledValue: ''
};
Alaska.predict = function(n, t) {
  clearTimeout(Alaska.predict.timer);
  Alaska.predict.timer = setTimeout(function() {
    Alaska.predictAjax(n, t)
  }, Alaska.predictVars.delayTime)
};
Alaska.predict.timer = null;
Alaska.predictAjax = function(n, t) {
  var i = Alaska.$(n).value.trim(), r = /^[a-z ]*$/i.test(i);
  getXHR() && i != '' && r ?
      (/*SURROGATE START:
          req.open("POST","/cities/"+t+"CitiesByPrefix?prefix="+i,!0),req.onreadystatechange=function(){if(Alaska.predictVars.predictCalled=!1,req.readyState==4&&req.status==200){try{data=JSON.parse(JSON.parse(req.responseText).msg)}catch(t){data=null}data===null||Alaska.$("input-selections-"+n)?data===null?Alaska.removeInputSelections(n):Alaska.updateInputSelections(data,n):Alaska.buildInputSelections(data,n)}},req.send("")
          SURROGATE END*/
       $miniwob.surrogateAutocomplete(
           i,
           function(data) {
             data === null || Alaska.$('input-selections-' + n) ?
                 data === null ? Alaska.removeInputSelections(n) :
                                 Alaska.updateInputSelections(data, n) :
                 Alaska.buildInputSelections(data, n)
           })) :
      Alaska.$('input-selections-' + n) && Alaska.removeInputSelections(n)
};
Alaska.geoASPub = function() {
  Alaska.geo(this.id, 'ASPublished')
};
Alaska.geoPartner = function() {
  Alaska.geo(this.id, 'Partners')
};
Alaska.geoCheckin = function() {
  Alaska.geo(this.id, 'Checkin')
};
Alaska.geo = function(n, t) {
  n = n.replace('-button', '');
  navigator.geolocation.getCurrentPosition(
      function(i) {
        getXHR() &&
            (req.open(
                 'POST',
                 '/cities/' + t + 'CitiesByLocation?longitude=' +
                     i.coords.longitude + '&latitude=' + i.coords.latitude,
                 !0),
             req.onreadystatechange = function() {
               var t, i;
               req.readyState == 4 &&
                   (req.status == 200 ?
                        (t = JSON.parse(req.responseText),
                         t.msg ? Alaska.util.showClientMsg(t.msg) :
                                 (i = JSON.parse(t.results),
                                  Alaska.buildInputSelections(i, n))) :
                        Alaska.util.showClientMsg(
                            'There are no airports near your current location that are served by Alaska Airlines.'))
             }, req.send(''))
      },
      function(n) {
        var t = '';
        switch (n.code) {
          case n.TIMEOUT:
            t = 'Request Timeout. Please try again.';
            break;
          case n.POSITION_UNAVAILABLE:
            t = 'Your current location is not available at this time.';
            break;
          case n.PERMISSION_DENIED:
            t = 'Please enable location services on your device.';
            break;
          case n.UNKNOWN_ERROR:
            t = 'Unknown error. Please try again.'
        }
        Alaska.util.showClientMsg(t)
      })
};
Alaska.updatePaymentOptions = function() {
  var n = Alaska.$('CreditCard_Id'), i = function() {
    var i, t;
    if (storedcc)
      if (i = Alaska.$('CCNum_Div'), hasModelError)
        i.style.display = n[n.selectedIndex].text.indexOf('(****') == -1 ||
                n[n.selectedIndex].text.indexOf('(****)') > -1 ?
            'block' :
            'none';
      else if (n.value == '' || n.value == 'NEW')
        Alaska.$('CreditCard_NameOnCard').value = '',
        Alaska.$('CreditCard_Number').value = '',
        Alaska.$('CreditCard_ExpirationMonth').value = '',
        Alaska.$('CreditCard_ExpirationYear').value = '',
        Alaska.$('CreditCard_CardType') &&
            (Alaska.$('CreditCard_CardType').value = ''),
        Alaska.$('CreditCard_HasStoredNumber') &&
            (Alaska.$('CreditCard_HasStoredNumber').value = 'false'),
        i.style.display = 'block';
      else
        for (t = 0; t < storedcc.length; t++)
          storedcc[t].Id == n.value &&
              (Alaska.$('CreditCard_NameOnCard').value = storedcc[t].NameOnCard,
               Alaska.$('CreditCard_Number').value = storedcc[t].Number,
               Alaska.$('CreditCard_ExpirationMonth').value =
                   storedcc[t].ExpirationMonth,
               Alaska.$('CreditCard_ExpirationYear').value =
                   storedcc[t].ExpirationYear,
               Alaska.$('CreditCard_CardType') &&
                   (Alaska.$('CreditCard_CardType').value =
                        storedcc[t].CardType),
               Alaska.$('CreditCard_HasStoredNumber') &&
                   (Alaska.$('CreditCard_HasStoredNumber').value =
                        storedcc[t].HasStoredNumber),
               i.style.display =
                   n[n.selectedIndex].text.indexOf('(****') == -1 ||
                       n[n.selectedIndex].text.indexOf('(****)') > -1 ?
                   'block' :
                   'none')
  }, t = Alaska.$('PhoneNumberDropdown'), r = function() {
    var n = Alaska.$('country-code'), i = Alaska.$('phone-number');
    t.value == 'NEW' ?
        (n.style.display = i.style.display = 'block',
         hasModelError ||
             (Alaska.$('PaymentPhoneNumber_CountryCode').value = '1',
              Alaska.$('PaymentPhoneNumber_Number').value = '')) :
        n.style.display = i.style.display = 'none'
  }, u, f;
  n && (Alaska.util.listenEvent(n, 'change', function(n) {
    n.preventDefault();
    i()
  }), i());
  t ? (Alaska.util.listenEvent(
           t, 'change',
           function(n) {
             n.preventDefault();
             r()
           }),
       r()) :
      (u = Alaska.$('country-code'), f = Alaska.$('phone-number'),
       u && f &&
           (Alaska.$('country-code').style.display =
                Alaska.$('phone-number').style.display = 'block'));
  hasModelError = !1
};
Alaska.swapStates = function(n) {
  var t = Alaska.$('uslist'), i = Alaska.$('calist'), r = Alaska.$('mxlist'),
      u = Alaska.$('nonelist');
  t.style.display = 'none';
  i.style.display = 'none';
  r.style.display = 'none';
  u.style.display = 'none';
  t.disabled = !0;
  i.disabled = !0;
  r.disabled = !0;
  u.disabled = !0;
  switch (n) {
    case 'US':
      t.style.display = 'block';
      t.disabled = !1;
      break;
    case 'CA':
      i.style.display = 'block';
      i.disabled = !1;
      break;
    case 'MX':
      r.style.display = 'block';
      r.disabled = !1;
      break;
    default:
      u.style.display = 'block';
      u.disabled = !1
  }
};
Alaska.util = {};
Alaska.util.getDocumentHeight = function() {
  var n = document;
  return Math.max(
      Math.max(n.body.scrollHeight, n.documentElement.scrollHeight),
      Math.max(n.body.offsetHeight, n.documentElement.offsetHeight),
      Math.max(n.body.clientHeight, n.documentElement.clientHeight))
};
Alaska.util.getParentByTagName = function(n, t) {
  var i = n.parentNode;
  return i ?
      i.tagName.toLowerCase() == t ? i : Alaska.util.getParentByTagName(i, t) :
      !1
};
Alaska.util.getElementsByClassName = function(n, t, i) {
  var r;
  return r = document.getElementsByClassName ?
             function(n, t, i) {
               var r, s;
               i = i || document;
               var f = i.getElementsByClassName(n),
                   e = t ? new RegExp('\\b' + t + '\\b', 'i') : null, o = [], u;
               for (r = 0, s = f.length; r < s; r += 1)
                 u = f[r], (!e || e.test(u.nodeName)) && o.push(u);
               return o
             } :
             document.evaluate ?
             function(n, t, i) {
               var r, c;
               t = t || '*';
               i = i || document;
               var e = n.split(' '), u = '', o = 'http://www.w3.org/1999/xhtml',
                   l = document.documentElement.namespaceURI === o ? o : null,
                   s = [], f, h;
               for (r = 0, c = e.length; r < c; r += 1)
                 u += '[contains(concat(\' \', @class, \' \'), \' ' + e[r] +
                     ' \')]';
               try {
                 f = document.evaluate('.//' + t + u, i, l, 0, null)
               } catch (a) {
                 f = document.evaluate('.//' + t + u, i, null, 0, null)
               }
               while (h = f.iterateNext()) s.push(h);
               return s
             } :
             function(n, t, i) {
               var u, a, f, v, e, y;
               t = t || '*';
               i = i || document;
               var h = n.split(' '), o = [],
                   c = t === '*' && i.all ? i.all : i.getElementsByTagName(t),
                   s, l = [], r;
               for (u = 0, a = h.length; u < a; u += 1)
                 o.push(new RegExp('(^|\\s)' + h[u] + '(\\s|$)'));
               for (f = 0, v = c.length; f < v; f += 1) {
                 for (s = c[f], r = !1, e = 0, y = o.length; e < y; e += 1)
                   if (r = o[e].test(s.className), !r) break;
                 r && l.push(s)
               }
               return l
             },
         r(n, t, i)
};
Alaska.util.listenEvent = function(n, t, i) {
  var r = n.getAttribute('isEventAdded');
  r ||
      (n.addEventListener ? n.addEventListener(t, i, !1) :
           n.attachEvent  ? (t = 'on' + t, n.attachEvent(t, i)) :
                            n['on' + t] = i,
       n.setAttribute('isEventAdded', !0))
};
Alaska.util.removeListenEvent = function(n, t, i) {
  var r = n.getAttribute('isEventAdded');
  r && n.removeAttribute && n.removeAttribute('isEventAdded');
  n.removeEventListener ? n.removeEventListener(t, i, !1) :
      n.detachEvent     ? (t = 'on' + t, n.detachEvent(t, i)) :
                          n['on' + t] = null
};
Alaska.util.getEventTarget = function(n) {
  return n = n || window.event, n.target || n.srcElement
};
Alaska.util.removeClass = function(n, t) {
  var i = n.className;
  n.className = i.replace(t, '')
};
Alaska.util.addClass = function(n, t) {
  var i = n.className.indexOf(t);
  i === -1 && (n.className += ' ' + t)
};
Alaska.util.hasClass = function(n, t) {
  var i = n.className.indexOf(t);
  return i === -1 ? !1 : !0
};
Alaska.util.setCookie = function(n, t, i) {
  var r = new Date, u = r.getTime() + i * 864e6,
      f = n + '=' + t + ';expires=' + u;
  document.cookie = f
};
Alaska.util.showClientMsg = function(n) {
  var t = Alaska.$('client-msg-div');
  t.className = 'server-msg-error';
  t.textContent = n
};
Alaska.util.hideClientMsg = function() {
  var n = Alaska.$('client-msg-div');
  n.className = '';
  n.innerHTML = ''
};
Alaska.util.whichDevice = function() {
  function n(n) {
    switch (!0) {
      case /BlackBerry/.test(n):
        return 'BlackBerry';
      case /iPhone/.test(n):
        return 'iOS';
      case /iPod/.test(n):
        return 'iOS';
      case /iPad/.test(n):
        return 'iOS';
      case /Android/.test(n):
        return 'Android';
      case /IEMobile/.test(n):
        return 'Windows';
      default:
        return 'other'
    }
  }
  return n(navigator.userAgent)
};
Alaska.util.userAgentContain = function(n) {
  var t = new RegExp(n, 'i');
  return t.test(navigator.userAgent)
};
Alaska.util.saveSelectedIndex = function(n, t) {
  Alaska.$(t).value = n.selectedIndex
};
Alaska.util.setSelectedText = function(n, t) {
  if (t.length > 0) {
    var i = Alaska.$(n);
    i.length > 0 && (i.selectedIndex = t)
  }
};
window.onload = function() {
  /*HEY THAT'S NOT COOL top!=self&&(top.location=self.location)*/
  ;
  Alaska.setup();
  Alaska.drop();
  Alaska.modal.init(
      'delete-alert', 'Confirm', 'Are you sure you want to delete this alert?',
      'No', 'Yes', '/flightalert/delete');
  Alaska.$('yesterday') && Alaska.cityPairDoesntDoYesterday();
  Alaska.$('payment-form') && Alaska.updatePaymentOptions();
  Alaska.$('contactinfo-form') &&
      (Alaska.contactinfosetup(), Alaska.updateContactInfos());
  Alaska.$('Contact_DestinationDescription') && Alaska.destinationinfosetup();
  Alaska.$('srh-is-miles') ||
      (Alaska.$('geo-from-wrap') &&
           Alaska.$('geo-from-button')
               .addEventListener('click', Alaska.geoASPub),
       Alaska.$('geo-to-wrap') &&
           Alaska.$('geo-to-button').addEventListener('click', Alaska.geoASPub),
       Alaska.$('geo-to') &&
           Alaska.$('geo-to').addEventListener('keyup', Alaska.predictASPub),
       Alaska.$('geo-from') &&
           Alaska.$('geo-from').addEventListener('keyup', Alaska.predictASPub));
  Alaska.$('bp-drop') && Alaska.persistentDrop();
  Alaska.$('offline-bp') || ShowProperAccordion();
  typeof runOmni != 'undefined' && runOmni && s.t()
};
Alaska.CitizenshipSelect = function(n, t, i) {
  var r = Alaska.$('Passengers_' + n + '__CitizenshipDocType'), e = !1, o = !1,
      u, f;
  if (r != null) {
    for (u = 0; u < r.length; u++)
      if (r[u].value == 'permanentresident' && (o = !0, t == 'US')) {
        e = !0;
        r.remove(u);
        break
      }
    e || o || i != 'True' ||
        (f = document.createElement('option'), f.text = 'US Resident Card',
         f.value = 'permanentresident', r.add(f, r[2]))
  }
};
Alaska.CitizenshipDocTypeSelect = function(n) {
  n == 'other' &&
      Alaska.modal.addStaticModal(
          'Airport Check-In required',
          'Your international documents must be verified prior to check-in.  <br /><br />Please check in with an Alaska Airlines Customer Service Agent at the airport.')
};
Alaska.CruiseLineTypeSelect = function(n) {
  Alaska.$('CruiseLineNameDiv').style.display = n == 'Other' ? 'block' : 'none'
};
Alaska.DestinationTypeSelect = function(n) {
  var t = Alaska.$('USDestinationAddress_Address'),
      i = Alaska.$('USDestinationAddress_Address1'), r;
  n == 'None' || n == 'Other' ?
      (Alaska.$('AddressDiv').style.display = 'none',
       t.value != '' && (i.value = t.value),
       Alaska.$('Address1Div').style.display = 'block',
       Alaska.$('Address2Div').style.display = 'block',
       Alaska.$('CityDiv').style.display = 'block',
       Alaska.$('CruiseLineDiv').style.display = 'none',
       Alaska.$('BusinessNameDiv').style.display = 'none',
       Alaska.$('HotelNameDiv').style.display = 'none',
       Alaska.$('DepartureCityDiv').style.display = 'none') :
      n == 'Residential' ?
      (Alaska.$('AddressDiv').style.display = 'none',
       Alaska.$('Address1Div').style.display = 'block',
       Alaska.$('Address2Div').style.display = 'block',
       t.value != '' && (i.value = t.value),
       Alaska.$('CityDiv').style.display = 'block',
       Alaska.$('CruiseLineDiv').style.display = 'none',
       Alaska.$('BusinessNameDiv').style.display = 'none',
       Alaska.$('HotelNameDiv').style.display = 'none',
       Alaska.$('DepartureCityDiv').style.display = 'none') :
      n == 'Hotel' ?
      (Alaska.$('HotelNameDiv').style.display = 'block',
       Alaska.$('CruiseLineDiv').style.display = 'none',
       Alaska.$('BusinessNameDiv').style.display = 'none',
       Alaska.$('AddressDiv').style.display = 'block',
       Alaska.$('Address1Div').style.display = 'none',
       Alaska.$('Address2Div').style.display = 'none',
       i.value != '' && (t.value = i.value),
       Alaska.$('CityDiv').style.display = 'block',
       Alaska.$('DepartureCityDiv').style.display = 'none') :
      n == 'Cruise' ?
      (Alaska.$('CruiseLineDiv').style.display = 'block',
       r = Alaska.$('USDestinationAddress_CruiseLine'),
       r.value == 'Other' &&
           (Alaska.$('CruiseLineNameDiv').style.display = 'block'),
       Alaska.$('DepartureCityDiv').style.display = 'block',
       Alaska.$('BusinessNameDiv').style.display = 'none',
       Alaska.$('HotelNameDiv').style.display = 'none',
       Alaska.$('AddressDiv').style.display = 'none',
       Alaska.$('Address1Div').style.display = 'none',
       Alaska.$('Address2Div').style.display = 'none',
       Alaska.$('CityDiv').style.display = 'none') :
      n == 'Business' &&
          (Alaska.$('BusinessNameDiv').style.display = 'block',
           Alaska.$('CruiseLineDiv').style.display = 'none',
           Alaska.$('HotelNameDiv').style.display = 'none',
           Alaska.$('AddressDiv').style.display = 'block',
           Alaska.$('Address1Div').style.display = 'none',
           Alaska.$('Address2Div').style.display = 'none',
           i.value != '' && (t.value = i.value),
           Alaska.$('CityDiv').style.display = 'block',
           Alaska.$('DepartureCityDiv').style.display = 'none')
};
Alaska.cogInfo = function() {
  Alaska.modal.addStaticModal(
      'Notice: Change of aircraft required',
      'For at least one of your flights, you must change aircraft en route even though your ticket may show only one flight number and have only one flight coupon for that flight. Further, in the case of some travel, one of your flights may not be identified at the airport by the number on your ticket, or it may be identified by other flight numbers in addition to the one on your ticket. At your request, the seller of this ticket will give you details of your change of aircraft, such as where it will occur and what aircraft types are involved.')
};
Alaska.Hazmat = function() {
  Alaska.modal.addStaticModal(
      'Hazardous materials',
      'US government regulations prohibit these hazardous materials on all aircraft. This includes items in your carry-on bags, checked bags and on your person.<br><br>Violating these regulations can result in imprisonment and heavy fines.<br><br>Alaska Airlines is required to report any hazardous materials confiscated in checked bags to the Federal Aviation Authority (FAA).<br><br>For the complete list of prohibited items, please visit faa.gov.')
};
Alaska.Firearms = function() {
  var n =
      '<ul>If you are checking bags that contain a firearm, you cannot self-tag your bag.<br><br>Firearms in checked bags must be:<br><br>';
  n += '<li class="firearmsmodal">Declared to a Customer Service Agent<\/li>';
  n += '<li class="firearmsmodal">Unloaded<\/li>';
  n += '<li class="firearmsmodal">Locked in a hard-sided case<\/li><br>';
  n += 'Get more info at tsa.gov.';
  Alaska.modal.addStaticModal('Firearms restrictions', n)
};
Alaska.VerificationCodeSent = function(n, t) {
  var i = 'We have sent an email to ' + t +
      '.<br/><br/>Use the link in the email to update your password.<br/><br/>NOTE: The link is valid for 30 minutes.';
  Alaska.modal.addRedirectModal(n, 'Email sent', i)
};
Alaska.UserIDSent = function(n, t) {
  var i = 'Your user ID was sent to ' + t +
      '. You may now close this window and continue with sign in.<br/><br/>Use the password you created when you set up your My Account profile.';
  Alaska.modal.addRedirectModal(n, 'Email sent', i)
};
Alaska.PremiumClassSeatsConfirmation = function() {
  Alaska.modal.addStaticModal(null, s)
};
Alaska.Wayfinding = function(n, t, i) {
  var r = '<ul>';
  n &&
      (r +=
       '<li class="wayfindingmodal"><b style="text-Decoration:underline;">Checking bags?<\/b> Print your bag tags at an airport kiosk, then drop them off at a baggage area.<\/li>');
  t &&
      (r +=
       '<li class="wayfindingmodal"><b style="text-Decoration:underline;">No bags to check?<\/b> You can head straight to the security line.<\/li>');
  i &&
      (r +=
       '<li class="wayfindingmodal"><b style="text-Decoration:underline;">Need help?<\/b> An Alaska Airlines customer service agent is standing by at the airport.<\/li>');
  r += '<ul>';
  Alaska.modal.addStaticModal('You\'re ready to go', r)
};
