#!/usr/bin/python3

# forms.py
# Date:  24/11/2020
# Author: Mihai Coșleț
# Email: coslet.mihai@gmail.com

"""
Form classes for use in views.
"""
from flask_wtf import FlaskForm
from wtforms import SelectField, StringField


class SearchForm(FlaskForm):
    keywords = StringField('Keywords', description="separate keywords with spaces")
    topic = SelectField('Topic', validate_choice=False)
    document_category = SelectField('Document Category', validate_choice=False)
    # start_date = DateField('Start Date', format="yyyy-mm-dd")
