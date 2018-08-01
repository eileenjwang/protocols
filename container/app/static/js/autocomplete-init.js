$( document ).ready(function() {

  $.getJSON( "/api/lookup", function( protocols ) {

    $('#protocols-autocomplete').autocomplete({
        lookup: protocols,
        groupBy: 'category',
        onSelect: function (suggestion) {
          window.location.href = suggestion.data.url;
        }
    });
  });


});
