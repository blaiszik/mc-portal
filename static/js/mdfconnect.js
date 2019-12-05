 $( document ).ready(function() {
        form_data = {}
        function update_form_data(){
          const moc_data = {
            services:{
                globus_publish:false,
                citrine: false,
                mrr:false
              },
            dc:{
                publicationYear:"2018",
                identifier: {
                      identifier: '10.test/1',
                      identifierType: 'DOI'
                    },
                publisher:"Materials Data Facility",
                subjects: [],
                titles: [],
                creators: [],
                descriptions: [],
                resourceType: {
                    resourceTypeGeneral: "Dataset"
                }
            },
            test: true,
            data:[]
          }

          // Format the title into dc
          moc_data.dc.titles.push({"title":$('#title').val()}) 

          // Format the authors
          authors = $('#authorPillbox').pillbox('items')
          for (var i = 0, l = authors.length; i < l; i++) {
            moc_data.dc.creators.push({"creatorName":authors[i].text})
          }

          // Format the data locations
          data_locations = $('#dataPillbox').pillbox('items')
          for (var i = 0, l = data_locations.length; i < l; i++) {
            console.log(data_locations[i].text);
            moc_data.data.push(data_locations[i].text)
          }

          // Format the institutions
          institutions = $('#insitutionPillbox').pillbox('items')
          for (var i = 0, l = institutions.length; i < l; i++) {
            console.log(institutions[i].text);
            moc_data.data.push(institutions[i].text)
          }

          // Format the tags
          tags = $('#tagsPillbox').pillbox('items')
          for (var i = 0, l = tags.length; i < l; i++) {
            moc_data.dc.subjects.push({"subject":tags[i].text})
          }

          // Format the services
          if ($("#publishCheck").is(":checked")){
            moc_data.services.globus_publish = true
          } 
          if ($("#mrrCheck").is(":checked")){
            moc_data.services.mrr = true
          }  
          if ($("#citrinationCheck").is(":checked")){
            moc_data.services.citrine = true
          }  
          console.log(moc_data)
          return moc_data
        }

      $('#authorPillbox').pillbox({"acceptKeyCodes":[13]});
      $('#institutionPillbox').pillbox({"acceptKeyCodes":[13]});
      $('#dataPillbox').pillbox({"acceptKeyCodes":[13]});
      $('#tagsPillbox').pillbox({"acceptKeyCodes":[13]});

      function validate_pillboxes(){
        valid = true

        title = $('#titleInput').val()
        if (!title){
          $('#titleLabel').addClass("invalid")
          valid = false
        }else{
          $('#titleLabel').removeClass("invalid")
        }

        authors = $('#authorPillbox').pillbox('items')
        if (authors.length == 0 ){
          $('#authorLabel').addClass("invalid")
          valid = false
        }else{
          $('#authorLabel').removeClass("invalid")
        }

        data_locations = $('#dataPillbox').pillbox('items')
        if (data_locations.length == 0 ){
          $('#dataLabel').addClass("invalid")
          valid = false
        }else{
          $('#dataLabel').removeClass("invalid")
        }

        return valid
     }

      function clear_form(){
        pillboxes  = [$("#dataPillbox"), 
                      $("#authorPillbox"), 
                      $("#tagsPillbox"), 
                      $("#institutionPillbox")]

        for (var i = 0, l = pillboxes.length; i < l; i++) {
          pillboxes[i].pillbox('removeItems');
        }

        $("#titleInput").val("")
     }

      $("#submit-button").click(function(){
        form_data = update_form_data();
        valid = validate_pillboxes();
        if (valid == true){
          console.log(form_data)
            $.ajax({
              url: '/api/convert',
              type: 'POST',
              contentType: 'application/json',
              data: JSON.stringify(form_data),
              dataType: 'json'
          }).done(function(data){
            console.log("done")
            console.log(data)
          })
            .success(function(data){
              console.log("success")
              console.log(data)
              $("#successAlert").addClass("visible")
              $("#successAlert").removeClass("invisible")
              clear_form()
          })
            .fail(function(err){
              console.log("error")
              console.log(err)
            });
        }
      })
    });