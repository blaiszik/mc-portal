from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, HiddenField
from wtforms.validators import DataRequired

class BoxSubmitForm(FlaskForm):
    auth = HiddenField('AuthKey')
    file_id = HiddenField('File ID')
    titleInput = StringField("Title", validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')
