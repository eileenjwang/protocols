$( document ).ready(function() {

  $.getJSON( "/lookup", function( protocols ) {

    $('#protocols-autocomplete').autocomplete({
        lookup: protocols,
        onSelect: function (suggestion) {
          window.location.href = suggestion.url;
        }
    });
  });


});
