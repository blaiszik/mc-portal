import React from "react";
import { render } from "react-dom";

const Form = JSONSchemaForm.default;

const schema = {
  "definitions": {
    "Thing": {
      "type": "object",
      "properties": {
        "name": {
          "type": "string",
          "default": "Default name"
        }
      }
    }
  },
  "type": "object",
  "properties": {
    "title": {
      "type": "string",
      "title": "Title"
    },

    "landing_page":{
      "type":"string",
      "title": "Landing Page"
    },

    "authors": {
      "type": "array",
      "title": "Authors",
      "items": {
        "type": "string"
        }
    },

    "institutions": {
      "type": "array",
      "title": "Institutions",
      "items": {
        "type": "string"
      }
    },

    "data_locations": {
      "description":"",
      "type": "array",
      "title": "Data Locations",
      "items": {
        "type": "string",
        "default": ""
      }
    },
    "associated_links": {
      "type": "array",
      "title": "Associated Links",
      "items": {
        "type": "string"
      }
    },


  }
};

const uiSchema = {
  "listOfStrings": {
    "items": {
      "ui:emptyValue": ""
    }
  },
  "associated_links":{
    "items":{
      "ui:placeholder":"http://dx.doi.org/12345"
    }
  },
  "institutions":{
    "items":{
      "ui:placeholder":"University of Chicago"
    }
  },
  "authors":{
    "items":{
      "ui:placeholder":"John Smith"
    }
  },
  "data_locations":{
    "items":{
      "ui:placeholder":"http://myhost.com/myfile.zip or globus://my_ep/my_path"
    }
  },
  "unorderable": {
    "ui:options": {
      "orderable": false
    }
  },
  "unremovable": {
    "ui:options": {
      "removable": false
    }
  },
  "noToolbar": {
    "ui:options": {
      "addable": false,
      "orderable": false,
      "removable": false
    }
  },
  "fixedNoToolbar": {
    "ui:options": {
      "addable": false,
      "orderable": false,
      "removable": false
    }
  }
};


const log = (type) => console.log.bind(console, type);

function submitData(data){

  function reqListener () {
    console.log(this.responseText);
  }

  console.log("As Received: ", data)

  const moc_data = {
    services:["globus_publish"],
    dc:{
        publicationYear:"2018",
        publisher:"Materials Data Facility",
        titles: [],
        creators: [],
        resourceType: {
            resourceTypeGeneral: "Dataset"
        }
    },
    data:{
      globus:""
    },
    mdf: {
        landing_page: "",
    }
  }

  // Format the title into dc
  moc_data.dc.titles.push({"title":data.formData.title})

  // Loop through authors and format them into dc
  const n_authors = data.formData.authors.length
  for (var i=0; i<n_authors; i++){
    moc_data.dc.creators.push({"creatorName":data.formData.authors[i]})
  }

  // Add the data location and landing page
  moc_data.data.globus = data.formData.data_locations[0]
  moc_data.mdf.landing_page = data.formData.landing_page

  console.log("As Sent: ", moc_data)

  //POST to the MOC server that is http proxied through the server to /api
  var moc_url = "/api/convert"
  var request = new XMLHttpRequest();
  request.addEventListener("load", reqListener);
  request.open('POST', moc_url, true);
  request.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');
  request.send(JSON.stringify(moc_data));
}

const onSubmit = ({formData}) => console.log("Data submitted: ",  formData);

render((<Form schema={schema}
        uiSchema={uiSchema}
        onChange={log('changes')}
        onSubmit={submitData}
        onError={log('errors')} />
), document.getElementById("app"));