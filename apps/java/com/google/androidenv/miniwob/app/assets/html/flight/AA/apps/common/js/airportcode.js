function launchAirportCode(fieldName, formName, nohref) {
  var modal_window_width;
  var modal_window_height;
  var width;
  var height;
  var leftdist;
  var topdist;
  width = screen.width;
  height = screen.height;
  modal_window_width = 750;
  modal_window_height = 500;
  leftdist = Math.round((width - modal_window_width) / 2);
  topdist = Math.round((height - modal_window_height) / 2);
  var newParam = '?jspEntry=\'yes\'';
  if (nohref) {
    newParam = '?nohref=\'yes\';';
  }
  eval(
      'document.getElementById(\'' + formName +
      '\').currentCodeForm.value = fieldName');
  eval(
      'document.getElementById(\'' + formName +
      '\').currentCalForm.value = formName');
  trackEvent('Airport lookup event requested');
  var codeWin = eval(window.open(
      '/reservation/airportLookup.do' + newParam, formName,
      'width=' + modal_window_width + ',height=' + modal_window_height +
          ',top=' + topdist + ',left=' + leftdist + ',scrollbars=yes,menu=no'));
}
var formReturn = window.name;
function setAirportCode(code) {
  preField = eval(
      'window.opener.document.getElementById(\'' + formReturn +
      '\').currentCodeForm.value');
  window.opener.document.getElementById(formReturn + '.' + preField).value =
      code;
  var labels =
      window.opener.jQuery('[name=\'' + preField + '\']').prevAll('span.value');
  if (labels.hasClass('hidden') == false) {
    labels.hide();
  }
  window.close();
}