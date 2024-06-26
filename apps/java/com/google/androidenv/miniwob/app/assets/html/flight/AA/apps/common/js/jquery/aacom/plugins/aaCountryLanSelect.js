jQuery.countryLanguageSelector = function() {
  var self = this;
  jQuery('#aa-country-selector').change(function() {
    jQuery('select#aa-language-selector').html('');
    var jsonData = '{ "locale": "' + this.value + '" }';
    jQuery.ajax({
      type: 'POST',
      url: '/home/ajax/languageLookup',
      data: jsonData,
      contentType: 'application/json; charset=UTF-8',
      async: true,
      cache: false,
      timeout: 60000,
      dataType: 'json',
      success: function(ajaxResponse, textStatus, xhr) {
        values = ajaxResponse.data.languages;
        options = '';
        for (var i = 0; i < values.length; i++) {
          options += '<option value="' + values[i].code + '">' +
              values[i].name + '</option>';
        }
        jQuery('select#aa-language-selector').html(options);
        self.changeAlert();
      }
    });
  });
  jQuery('#aa-language-selector').change(function() {
    self.changeAlert();
  });
  jQuery('#splashForm').submit(function() {
    url = jQuery('select#aa-language-selector', this).val();
    jQuery('#splashSelectedCountry', this)
        .val(self.getParameter(url, 'locale'));
    jQuery('#splashUrl', this).val(self.getParameter(url, 'url'));
    jQuery('#splashGeoRedirect', this)
        .val(self.getParameter(url, 'georedirect'));
  });
  self.getParameter = function(url, name) {
    return decodeURIComponent(
        (RegExp(name + '=(.+?)(&|$)').exec(url) || [, ''])[1]);
  };
  self.changeAlert = function() {
    if (self.getParameter(
            jQuery('select#aa-language-selector').val(), 'locale') !=
        jQuery('input#currentLocale').val()) {
      jQuery('#locale-change-alert').slideDown();
    } else {
      jQuery('#locale-change-alert').hide('fast');
    }
  };
};