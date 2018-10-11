from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, HiddenField
from wtforms.validators import DataRequired
from mdf_connect_client.mdfcc import MDFConnectClient
from wtforms.widgets import TextArea

class DatasetSubmitForm(FlaskForm):
    auth = HiddenField('AuthKey')
    file_id = HiddenField('File ID')
    titleInput = StringField("Title")
    authors = HiddenField("Authors")
    institutions = HiddenField("Institutions")
    publication_year = StringField("Publication Year")
    data_locations = HiddenField("Data Locations")
    description = StringField("Description", widget=TextArea())
    submit = SubmitField('Publish')

    is_explicit_data_location = True
    form_action = "/publish/box/do_publish"

    def add_dc(self, mdf: MDFConnectClient):
        mdf.create_dc_block(
            title=self.titleInput.data,
            authors=self.authors.data.split("\t"),
            affiliations=self.institutions.data.split("\t"),
            description=self.description.data,
            publication_year=self.publication_year.data
        )

    def add_data(self, mdf: MDFConnectClient):
        mdf.add_data(self.data_locations.data.split("\t"))
