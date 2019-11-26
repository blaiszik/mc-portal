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
                "subjects": [],
                "related_dois":[]
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
            "doi":"",
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
        fetch_doi(){
            console.log("Fetching DOI")
            self = this
            console.log(this.state)
            axios.post('/api/doi', {"doi":self.state.doi})
            .then(function(response){
                console.log(response)
                self.form.dc.authors = response.data[0].authors
                self.form.dc.title = response.data[0].title
                self.form.dc.related_dois.push(self.state.doi)
            })
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
                  "authors": [
                    "Su-Yang Ma",
                    "Qiong Ma",
                    "Yang Gao",
                    "Anshul Kogar",
                    "Guo Alfred Zong",
                    "Mier Valdivia, Andres M.",
                    "Thao H. Dinh",
                    "Shin-Ming Huang",
                    "Bahadur Singh",
                    "Chuang-Han Hsu",
                    "Tay-Rong Chang",
                    "Jacob P.C. Ruff",
                    "Kenji Watanabe",
                    "Takashi Taniguchi",
                    "Hsin Lin",
                    "Goran Karapetrov",
                    "Di Xiao",
                    "Pablo Jarillo-Herrero",
                    "Nuh Gedik"
                  ],
                  "affiliations": [
                    "Massachusetts Institute of Technology",
                    "National Sun Yat-sen University",
                    "Shenzhen University",
                    "Northeastern University",
                    "National University of Singapore",
                    "National Cheng Kung University",
                    "National Institute for Materials Science Japan",
                    "Academica Sinica",
                    "Drexel University",
                    "Carnegie Mellon University"
                  ],
                  "description": "Experimental data accompanying publication (Nature) \"Optical detection and manipulation of spontaneous gyrotropic electronic order in a transition-metal dichalcogenide semimetal\"\nThe experimental data were collected from four samples, grouped into their individual folders. *.ibw is Igor binary file and .pxp is Igor Packed Experiment file that contains Igor waves. They need to be opened with Igor Pro. Simple description of the data can be found from the name of the file and folder.",
                  "title": "Data sets for \"Optical detection and manipulation of spontaneous gyrotropic 1 electronic order in a transition-metal dichalcogenide semimetal\" Nature paper",
                  "subjects": [
                    "experiment",
                    "2D Material",
                    "Chiral photogalvanic current",
                    "Chiral electronic phases"
                  ]
                },
                "services": {
                  "mdf_publish": true,
                  "mrr": false,
                  "citrine": false
                },
                "contacts": [
                  "qiongm@mit.edu",
                  "heinonen@anl.gov"
                ],
                "source_name": "Qiong_TiSe2_Nature_20191120",
                "organizations": [
                  "MDF Open"
                ],
                "acl": "public",
                "data": [
                  "https://app.globus.org/file-manager?origin_id=17ddaece-20be-11e9-9835-0262a1f2f698"
                ],
                "test": false,
                "passthrough": false,
                "update": true
            }

        }
    }
})