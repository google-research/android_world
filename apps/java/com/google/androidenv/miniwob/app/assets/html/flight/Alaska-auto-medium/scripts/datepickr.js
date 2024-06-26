Alaska.$('lbldep-date').setAttribute('onclick', 'return false');
Alaska.$('lblret-date').setAttribute('onclick', 'return false');
Alaska.util.listenEvent(Alaska.$('departure-date'), 'focus', function() {
  Alaska.datepickrState = 0;
  this.blur();
  new Alaska.datepickr
});
Alaska.util.listenEvent(Alaska.$('return-date'), 'focus', function() {
  Alaska.datepickrState = 1;
  this.blur();
  new Alaska.datepickr
});
Alaska.datepickrState = 0;
Alaska.datepickr = function(n) {
  function i(n, t, i) {
    var r, u;
    if (n in tt || (tt[n] = document.createElement(n)), r = tt[n].cloneNode(!1),
        t != null)
      for (u in t) r[u] = t[u];
    return i != null &&
               (typeof i == 'object' ? r.appendChild(i) : r.innerHTML = i),
           r
  }
  function at(n, t) {
    return t == !0 ? y[n] : y[n].length > 3 ? y[n].substring(0, 3) : y[n]
  }
  function et() {
    for (currentMonthView < 0 && (currentYearView--, currentMonthView = 11),
         currentMonthView > 11 && (currentYearView++, currentMonthView = 0),
         Alaska.$('prev-month').className = p() ? 'hide' : '',
         Alaska.$('next-month').className = w() ? 'hide' : '',
         d.innerHTML =
             l.month.string(o.fullCurrentMonth) + ' ' + currentYearView;
         e.hasChildNodes();)
      e.removeChild(e.lastChild);
    return e.appendChild(ct()), ot(), rt(), !1
  }
  function vt() {
    g.onclick = function() {
      return p() ? !1 : (currentMonthView--, et())
    };
    nt.onclick = function() {
      return w() ? !1 : (currentMonthView++, et())
    }
  }
  function ot() {
    var n = e.getElementsByTagName('a'), i = n.length;
    for (t = 0; t < i; t++)
      n[t].onclick = function() {
        for (var f, e, t = 0; t < i; t++) n[t].className = 'cal-day';
        return f = currentMonthView + 1 + '/' + this.innerHTML + '/' +
                   currentYearView,
               e = new Date(currentYearView, currentMonthView, this.innerHTML),
               Alaska.datepickrState == 0 ?
                   (r = e, b.value = f, b.className = 'text-input calbg') :
                   (u = e, k.value = f, k.className = 'text-input calbg'),
               rt(), !1
      }
  }
  function it(n) {
    for (var t = 0, i = n.length; t < i; t++)
      n[t].className = 'cal-day selected'
  }
  function st(n) {
    for (var i = u.getDate(), t = 0, r = n.length; t < r; t++)
      n[t].innerHTML <= i && (n[t].className = 'cal-day selected')
  }
  function ht(n) {
    for (var i = r.getDate(), t = 0, u = n.length; t < u; t++)
      n[t].innerHTML >= i && (n[t].className = 'cal-day selected')
  }
  function rt() {
    var t = e.getElementsByTagName('a'), o = t.length, i, f, n;
    if (r != null && u != null)
      if (i = r.getMonth(), f = u.getMonth(), currentMonthView == i && i == f)
        for (n = 0; n < o; n++)
          t[n].innerHTML >= r.getDate() && t[n].innerHTML <= u.getDate() &&
              (t[n].className = 'cal-day selected');
      else
        r.getFullYear() != u.getFullYear() ? currentMonthView <= 11 &&
                currentYearView<
                    u.getFullYear() ? currentMonthView == i ?
                                      ht(t) :
                                      currentMonthView > i && it(t) :
                                      currentYearView>r.getFullYear() &&
                currentYearView <= u.getFullYear() && currentMonthView <= f &&
                (currentMonthView == f ? st(t) : it(t)) :
            i == currentMonthView && i < f ? ht(t) :
                                             i != currentMonthView && i < f &&
                currentMonthView <= f &&
                (currentMonthView == f ? st(t) : currentMonthView > i && it(t));
    if (r != null && r.getMonth() == currentMonthView)
      for (n = 0; n < o; n++)
        if (t[n].innerHTML == r.getDate()) {
          t[n].className = 'cal-day selectedlight';
          break
        }
    if (u != null && u.getMonth() == currentMonthView)
      for (n = 0; n < o; n++)
        if (t[n].innerHTML == u.getDate()) {
          t[n].className = 'cal-day selecteddark';
          break
        }
  }
  function yt() {
    var n = document.createDocumentFragment();
    for (t = 0, ft = ut.length; t < ft; t++) n.appendChild(i('th', {}, ut[t]));
    return n
  }
  function p() {
    return currentMonthView == v.getMonth()
  }
  function pt() {
    return currentYearView == v.getFullYear()
  }
  function w() {
    return currentMonthView == c.getMonth()
  }
  function wt() {
    return currentYearView == c.getFullYear()
  }
  function ct() {
    var f = new Date(currentYearView, currentMonthView, 1).getDay(),
        e = l.month.numDays(), r = 0, u = document.createDocumentFragment(),
        n = i('tr');
    for (t = 1; t <= f; t++) n.appendChild(i('td', {}, '&nbsp;')), r++;
    for (t = 1; t <= e; t++)
      r == 7 && (u.appendChild(n), n = i('tr'), r = 0),
          w() && c.getDate() <= t && wt() || p() && v.getDate() > t && pt() ?
          n.appendChild(i('td', {}, t)) :
          n.appendChild(
              i('td', {}, i('a', {className: 'cal-day', href: '#'}, t))),
          r++;
    for (t = 1; t <= 7 - r; t++) n.appendChild(i('td', {}, '&nbsp;'));
    return u.appendChild(n), u
  }
  function bt(n) {
    var u, r, f, h, v, t, y, b, c, a;
    if (n)
      for (u in n) o.hasOwnProperty(u) && (o[u] = n[u]);
    r = document.createElement('div');
    r.setAttribute('id', 'modal-background');
    r.setAttribute(
        'style', 'height: ' + Alaska.util.getDocumentHeight() + 'px;');
    r.setAttribute('class', 'disable-ui');
    f = document.createElement('div');
    f.setAttribute('id', 'cal-modal-window');
    h = document.createElement('div');
    v = Alaska.datepickrState == 0 ? 'departure' : 'return';
    h.setAttribute('class', 'highlight');
    h.innerHTML = '<div class=\'title\'>Select <span id=\'cal-top-text\'>' + v +
        '<\/span> date<\/div>';
    s = i('div', {id: 'cal'});
    t = i('div', {className: 'months'});
    g =
        i('span', {id: 'prev-month', className: p() ? 'hide' : ''},
          i('a', {href: '#'}, '&nbsp;&nbsp;'));
    nt =
        i('span', {id: 'next-month', className: w() ? 'hide' : ''},
          i('a', {href: '#'}, '&nbsp;&nbsp;'));
    d =
        i('span', {className: 'current-month'},
          l.month.string(o.fullCurrentMonth) + ' ' + currentYearView);
    t.appendChild(d);
    y = i('span', {id: 'next-month-pad'});
    t.appendChild(y);
    t.appendChild(nt);
    b = i('span', {id: 'prev-month-pad'});
    t.appendChild(b);
    t.appendChild(g);
    c = i('table', {}, i('thead', {}, i('tr', {className: 'weekdays'}, yt())));
    e = i('tbody', {}, ct());
    c.appendChild(e);
    s.appendChild(h);
    s.appendChild(t);
    s.appendChild(c);
    a = document.createElement('div');
    a.innerHTML =
        '<div id="btnDone" onclick="Alaska.datepickrDone();" class="button-link">Done<\/div>';
    s.appendChild(a);
    f.appendChild(s);
    r.appendChild(f);
    document.body.appendChild(r);
    Alaska.datepickrReCalc();
    vt();
    ot();
    rt()
  }
  var o = {daysLowerLimit: 0, daysUpperLimit: 332, fullCurrentMonth: !0},
      f = new Date(Alaska.$('server-date').value),
      h = Alaska.$('departure-date').value != '' ?
      new Date(Alaska.$('departure-date').value) :
      null,
      a = Alaska.$('return-date').value != '' ?
      new Date(Alaska.$('return-date').value) :
      null,
      v = new Date(f.getTime() + o.daysLowerLimit * 864e5),
      c = new Date(f.getTime() + o.daysUpperLimit * 864e5),
      r = h != null && h >= f && h >= v && h <= c ? h : null,
      u = a != null && a >= f && a <= c ? a : null, l = {
        month: {
          integer: function() {
            return currentMonthView
          },
          string: function(n) {
            var t = currentMonthView;
            return at(t, n)
          },
          numDays: function() {
            return l.month.integer() == 1 && !(currentYearView & 3) &&
                    (currentYearView % 100 || !(currentYearView % 400)) ?
                29 :
                lt[l.month.integer()]
          }
        }
      },
      ut = ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa'],
      y =
          [
            'January', 'February', 'March', 'April', 'May', 'June', 'July',
            'August', 'September', 'October', 'November', 'December'
          ],
      lt = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31], b, k, s, e, d, g,
      nt, t, ft, tt = [];
  return Alaska.datepickrState == 0 ?
             (currentYearView = r != null ? r.getFullYear() : f.getFullYear(),
              currentMonthView = r != null ? r.getMonth() : f.getMonth()) :
             (currentYearView = u != null ? u.getFullYear() :
                  r != null               ? r.getFullYear() :
                                            f.getFullYear(),
              currentMonthView = u != null ? u.getMonth() :
                  r != null                ? r.getMonth() :
                                             f.getMonth()),
         Alaska.datepickrFormDisable(!0), function() {
           b = Alaska.$('departure-date');
           k = Alaska.$('return-date');
           bt(n)
         }()
};
Alaska.datepickrReCalc = function() {
  var n = Alaska.modal.calculateTop(Alaska.$('cal-modal-window')), t;
  Alaska.util.userAgentContain('ALKApp/iOS') &&
      (t = n.length - 2, n = n.substring(0, t) - 60 + 'px');
  Alaska.$('cal-modal-window').setAttribute('style', 'top: ' + n + ';')
};
Alaska.datepickrDone = function() {
  Alaska.datepickrFormDisable(!1);
  Alaska.modal.remove();
  window.removeEventListener('resize', Alaska.datepickrReCalc)
};
Alaska.datepickrFormDisable = function(n) {
  var i, t, r;
  if (1)
    for (i = Alaska.$('searchForm').elements, t = 0, r = i.length; t < r; t++)
      i[t].disabled = n
};
