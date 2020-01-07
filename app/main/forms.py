from flask_wtf import FlaskForm
from flask_babel import lazy_gettext as _l
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length

    
class EditProfileForm(FlaskForm):
    username = StringField(_l('Username'), validators=[Length(min=0,max=50)])
    about_me = TextAreaField(_l('About me'), validators=[Length(min=0,max=150)])
    pwd = PasswordField(_l('Password'), validators=[DataRequired()])
    submit = SubmitField(_l('Submit'))

class PostForm(FlaskForm):
    post = TextAreaField(_l('Say something'), validators=[
        DataRequired(), Length(min=1, max=140)])
    submit = SubmitField(_l('Submit'))