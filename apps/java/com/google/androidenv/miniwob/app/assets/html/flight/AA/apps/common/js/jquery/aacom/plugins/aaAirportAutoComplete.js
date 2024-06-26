(function($j) {
function aaAirportAutoComplete(targetFields, onlyAirportsIfNotNull, options) {
  var defaults = {
    minLength: 3,
    source: function(request, response) {
      $miniwob.surrogateAutocomplete({
        type: 'GET',
        url: '/home/ajax/airportLookup',
        contentType: 'application/json',
        dataType: 'json',
        data: {
          searchText: request.term,
          onlyAirportsIfNotNull: onlyAirportsIfNotNull
        },
        success: function(data) {
          response($j.map(data, function(item) {
            return {
              label: item.code + ' - ' + item.name + ', ' +
                  (item.countryCode == 'US' ? item.stateCode :
                                              item.countryName),
              value: item.code
            };
          }));
        }
      });
    },
    messages: {
      noResults: function() {
        return AAcom.prototype.getProperty('autoComplete.noResult');
      },
      results: function(count) {
        var resultMessage = '';
        if (count === 1) {
          resultMessage = AAcom.prototype.getProperty('autoComplete.oneResult');
        } else {
          resultMessage =
              AAcom.prototype.getProperty('autoComplete.manyResult');
          resultMessage = resultMessage.replace('{0}', count);
        }
        return resultMessage;
      }
    },
    select: function() {
      $j(this).blur().focus();
    },
    focus: function(event, ui) {
      $j('#ariaLiveReaderContainer').text(ui.item.label);
    }
  };
  var settings = $j.extend(defaults, options);
  $j(targetFields).autocomplete(settings).attr({
    autocomplete: 'off',
    autocorrect: 'off'
  });
}
$j.fn.aaAirportAutoComplete = function(onlyAirportsIfNotNull, options) {
  return this.each(function() {
    new aaAirportAutoComplete(this, onlyAirportsIfNotNull, options);
  });
};
}(jQuery));
