from wtforms import Form, fields, validators


class LoginForm(Form):
    email = fields.StringField('User Email', [validators.DataRequired(), validators.Email()])
    password = fields.StringField('User Password', [validators.DataRequired(), validators.Length(min=3, max=20)])


class SignUpForm(LoginForm):
    full_name = fields.StringField('Username', [validators.DataRequired(), validators.Length(min=3, max=20)])


class MessageForm(Form):
    text = fields.StringField('Text', [validators.DataRequired()])
