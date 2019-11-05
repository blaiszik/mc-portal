Vue.use(Vuetify)

new Vue({
    el: '#app',
    vuetify: new Vuetify(),
    data: () => ({
        options: {
            "subjects": ["simulation", "experiment", "machine learning",
                         "metals and alloys", "polymers", 
                         "semiconductors", "energy materials",
                        "composites", "ceramics", "oxides", "metallic glasses", 
                        "biomaterials","metamaterials","defects","diffusion", 
                        "molecular structures", "morphologies", 
                        "high-throughput",
                        "microscopy","spectroscopy", "microstructures",
                        "DFT", "QMCPack", "QMC", "Monte Carlo", 
                        "EBSD"],
            "affiliations": ["University of Chicago", 
                             "Northwestern University",
                             "Argonne National Laboratory", 
                             "University of Illinois at Urbana-Champaign", 
                             "North Carolina State", 
                             "Oak Ridge National Laboratory"],
            "organizations": ["MDF Open", 
                              "Center for Hierarchical Materials Design (CHiMaD)", 
                              "Center for Predictive Simulation of Functional Materials (CPSFM)",
                              "AFRL Additive Manufacturing Challenge"
                            ],
            "services": [{
                    title: 'MDF Publish',
                    desc: "MDF Publish is a service that enables users to receive a citable identifier (e.g., DOI) and to automatically move data to long-term storage for ease of access by other users. ",
                    flex: 12,
                    label: "",
                    img: "https://materialsdatafacility.org/images/MDF-logo@2x.png",
                    value: "mdf_publish"
                },
                {
                    title: 'Materials Resource Registry',
desc:"This system allows for the registration of materials resources, bridging the gap between existing resources and the end users. The Materials Resource Registry functions as a centrally located service, making the registered information available for research to the materials community.",                            flex: 12,
                    label: "",
                    img:"/static/img/nist-dark.png",
                    value: "mrr"
                },
                {
                    title: 'Citrination',
                    desc:"The platform enables researchers to share open data in a findable, accessible, interoperable, and reusable format, at no cost. They also have the option to keep their data completely confidential..The Open Citrination Platform is complimentary for university and select non-profit researchers.",
                    flex: 12,
                    label: "",
                    img:"https://1hrkl410nh36441q7v2112ft-wpengine.netdna-ssl.com/wp-content/uploads/2018/07/Citrine-informatics-logo.svg",
                    value: "citrine"
                }
            ]
        },
        rules: {
            "title": [v => !!v || 'Title is required'],
            "combo": [v => !!v.length || 'This field is required']
        },
        form: {
            "dc": {
                "authors": [],
                "affiliations": [],
                "description": "",
                "title": "",
                "subjects": []
            },
            "services":{
                "mdf_publish": false,
                "mrr": false,
                "citrine": false
            },
            contacts:[],
            source_name:"",
            organizations: ["MDF Open"],
            acl: "public",
            data: [],
            test: true,
            passthrough: true
        },
        state: {
            "spinner":false,
            "valid": true,
            "submit_success":false,
            "submission_id":null,
            "items": [],
            "markdown": "",
            "response":null,
            "debug":false
        }
    }),

    methods: {
        validate() {
            if (this.$refs.form.validate()) {
                this.snackbar = true
            }
        },
        remove_item(item, path){
            var val = _.get(this, path);
            console.log(val)
            val.splice(val.indexOf(item),1)
            _.set(this, path, [...val])
            console.log(_.get(this, path));
        },
        update_markdown(v) {
            console.log(v)
            this.state.markdown = marked(v, {
                sanitize: true
            })
            console.log(this.state.markdown)
        },
        submit_dataset(v) {
            var self = this;
            if(self.$refs.form.validate()){
                self.state.spinner = true
                // Make a request for a user with a given ID
                console.log(this.form)
                axios.post('/api/convert', this.form)
                    .then(function (response) {
                        // handle success
                        console.log("Success")
                        console.log(response);
                        self.state.submit_success = true
                        self.state.submission_id = response.source_id
                        self.state.response = response
                        self.state.spinner = false
                    })
                    .catch(function (error) {
                        // handle error
                        console.log("Error")
                        self.state.submit_success = false
                        self.state.spinner = false
                        self.state.response = error.response
                        console.log(error.response);
                    })
                    .then(function () {
                        console.log(self)
                        // always executed
                    });
            }else{
                self.state.valid = false
                console.log("INVALID")
            }
        },
        fill_dummy_data(){
            function makeid(length) {
                var result           = '';
                var characters       = 'abcdefghijklmnopqrstuvwxyz0123456789';
                for ( var i = 0; i < length; i++ ) {
                   result += characters.charAt(Math.floor(Math.random() * characters.length));
                }
                return result;
             }

            this.form = {
                "dc": { 
                    "authors": [ "Emily Mayer", "Clayton S. Talbot", "Nunez, Victoria"], 
	                "affiliations": [ "University of Chicago", "Argonne National Laboratory" ], 
	                "description": "", 
	                "title": "In Situ Observation Dendrite Formation in Cu-Sn Alloys " + makeid(7), 
	                "subjects": [ "experiment", "machine learning","metals and alloys"] }, 
	                "services": { 
                        "mdf_publish": true, 
                        "mrr": false, 
                        "citrine": false 
                    }, 
                    "contacts":["Victoria Nunez <nunez.xyz@uchicago.edu>"],
                    "acl": "public",
                    "data": [ "https://app.globus.org/file-manager?origin_id=e38ee745-6d04-11e5-ba46-22000b92c6ec&origin_path=%2Fcitrine_mdf_demo%2Falloy.pbe%2FAg%2FAg.F4%2F" ],
                    "organizations":"MDF Open",
                    "test": true,
                    "passthrough": false,
                    "update":false
            }

        }
    }
})