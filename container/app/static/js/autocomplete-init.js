$( document ).ready(function() {

  $.getJSON( "/api/lookup", function( protocols ) {

    $('#protocols-autocomplete').autocomplete({
        lookup: protocols,
        onSelect: function (suggestion) {
          window.location.href = suggestion.url;
        }
    });
  });


});
