from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired


class PostForm(FlaskForm):
    title = StringField('Nadpis', validators=[DataRequired()])
    url = StringField('URL článku', validators=[DataRequired()])
    content = TextAreaField('Text', validators=[DataRequired()])
    submit = SubmitField('Opýtať')


class ResponseForm(FlaskForm):
    message = TextAreaField('Odpoveď', validators=[DataRequired()])
    submit = SubmitField('Odpovedať')