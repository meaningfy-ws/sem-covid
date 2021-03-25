#!/usr/bin/python3

# forms.py
# Date:  24/11/2020
# Author: Mihai Coșleț
# Email: coslet.mihai@gmail.com

"""
Form classes for use in views.
"""
from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import RadioField, StringField, SelectField
from wtforms.validators import DataRequired


class SearchForm(FlaskForm):
    topic = SelectField('Topic', validate_choice=False)
    stage = SelectField('Stage', validate_choice=False)
    act_type = SelectField('Act Type', validate_choice=False)
