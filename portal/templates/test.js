$( document ).ready(function() {
    console.log( "ready2!" );
    $('body').off('fu.data-api')


    $('#institutionPillbox').pillbox({"acceptKeyCodes":[13, 186]});
    $('#institutionPillbox').on('added.fu.pillbox edited.fu.pillbox removed.fu.pillbox', 
                                        function pillboxChanged() {
                                          $('#pillboxInput').val( JSON.stringify( $('#institutionPillbox').pillbox('items') )  );
                                          console.log($('#pillboxInput').val()););
});