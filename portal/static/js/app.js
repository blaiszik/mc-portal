import React from "react";
import ReactDOM from 'react-dom';

import { render } from "react-dom";
import { Alert } from "react-bootstrap";

import axios from "axios";


const Form = JSONSchemaForm.default;

const schema = {
  "type":"object",
  "required": ["title", "authors", "data_locations"],
  "properties": {
    "title": {
      "type": "string",
      "title": "Title"
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
      "description":"Identify the location of the dataset on a web server or on a Globus endpoint",
      "type": "array",
      "title": "Data Locations",
      "items": {
        "type": "string",
        "default": "",
        "pattern":"^(https?|globus)://"
      }
    },
    "associated_links": {
      "type": "array",
      "description": "List of other works associated with this dataset.",
      "title": "Associated Links",
      "items": {
        "type": "string"
      }
    },
    "services": {
      "type": "array",
      "description": "Attempt to convert, and share this data with the selected services.",
      "title": "Register Data With",
      "items": {
        "type": "string",
        "enum": [
          "MDF Publish",
          "Citrination"
        ]
      },
      "uniqueItems": true
    }
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
  "multipleChoicesList": {
    "ui:widget": "checkboxes"
  },
  "services": {
    "ui:widget": "checkboxes"
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

function format_form_data(data){
    const moc_data = {
      services:[],
      dc:{
          publicationYear:"2018",
          identifier: {
          			identifier: '10.test/1',
          			identifierType: 'DOI'
          		},
          publisher:"Materials Data Facility",
          titles: [],
          creators: [],
          resourceType: {
              resourceTypeGeneral: "Dataset"
          }
      },
      data:[]
    }

    // Format the title into dc
    moc_data.dc.titles.push({"title":data.title})

    console.log(data)
    if (data.services instanceof Array){
      if (data.services.includes("MDF Publish")){
        moc_data.services.push("globus_publish")
       }
      if (data.services.includes("Citrination")){
        moc_data.services.push("citrine")
      }
    }else{
      moc_data.services = []
    }



    // Loop through authors and format them into dc
    const n_authors = data.authors.length
    for (var i=0; i<n_authors; i++){
      moc_data.dc.creators.push({"creatorName":data.authors[i]})
    }


    // Loop through data locations and add them
    const n_locations = data.data_locations.length
    for (var i=0; i<n_locations; i++){
      moc_data.data.push(data.data_locations[i])
    }

    return moc_data
}

const step1schema = {
  title: "Step 1",
  type: "object",
  required: ["name"],
  properties: {
  	name: {type: "string", minLength: 3},
  }
};
const step2schema = {
  title: "Dataset Submitted",
  type: "object",
  required: ["age"],
  properties: {
    age: {type: "integer"}
  }
};

class App extends React.Component {
  constructor(props) {
    super(props);
    this.state = {step: 1,
                  submitted:false,
                  source_name: '',
                  moc:{},
                  formData: {}};
  }

  onSubmit = ({formData}) => {
  	if (this.state.step === 1) {
      console.log(JSON.stringify(format_form_data(formData), null, 2))
        //POST to the MOC server that is http proxied through the server to /api
        var moc_url = "/api/convert"
        // Make a request for a user with a given ID
        axios.post(moc_url, format_form_data(formData))
          .then((response) => {
            console.log(response.data.source_name);
            this.setState({submitted:response.data.success, source_name:response.data.source_name});
            console.log(this.state);
          })
          .catch( (error) => {
            console.log(error);
          });
    }
  }

  render() {
    return (
      <div>
      <Form
        schema={this.state.step === 1 ? schema : {"title":"ABC"}}
        uiSchema={uiSchema}
        onSubmit={this.onSubmit}
        formData={this.state.formData}/>
      <StatusView source_name={this.state.source_name} />
      </div>
    );
  }
}

class StatusView extends React.Component {
  constructor(props) {
    super(props);
    this.state = {source_name:this.props.source_name};
  }

  updateStatus(){
    console.log("updating status")
  }

  render(){
    if (this.props.source_name){
      return (<div>
            <h1> Dataset Submitted </h1>
              <h3>
                <div className="alert alert-success">
                  <a className="button button-primary button-lg" href={'/status/'+this.props.source_name}>
                    Re-Check Submission Status
                  </a>
                </div>
              </h3>
              <StatusCheck source_name={this.props.source_name} />
            </div>);
    }else{
      return(<div></div>);
    }

    // return(<div>
    //       <a href={'/api/status/'+this.props.source_name}>Check Submission Status</a>
    //       </div>);
  }
};

class StatusCheck extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
                source_name:this.props.source_name,
                status_message:""
    };

    var moc_url = "/api/status"
    if (this.state.source_name){
      axios.get(moc_url+'/'+this.state.source_name)
        .then((response) => {
          console.log("Checking Status")
          console.log(response);
          this.setState({status_message:response.data.status_message.replace(/\n/g, '<br />')});
          console.log(this.state);
        })
        .catch( (error) => {
          console.log(error);
        });
    }
  }

  render(){
    return(<div dangerouslySetInnerHTML={{__html:this.state.status_message}}>

           </div>);
  }
}


ReactDOM.render(<App />,
  document.getElementById('app')
);
