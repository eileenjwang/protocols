$( document ).ready(function() {
  console.log('Autocomplete-init.js loaded');

  $.getJSON( "/lookup", function( protocols ) {
    // var protocols = [
    //    { value: 'Andorra', data: 'AD' },
    //    // ...
    //    { value: 'Zimbabwe', data: 'ZZ' }
    // ];
    console.log(protocols);

    $('#protocols-autocomplete').autocomplete({
        lookup: protocols,
        onSelect: function (suggestion) {
          window.location.href = suggestion.url;
            // alert('You selected: ' + suggestion.value + ', ' + suggestion.id);
        }
    });
    // var items = [];
    // $.each( data, function( key, val ) {
    //   items.push( "<li id='" + key + "'>" + val + "</li>" );
    // });
    //
    // $( "<ul/>", {
    //   "class": "my-new-list",
    //   html: items.join( "" )
    // }).appendTo( "body" );
  });


});
