#
# This file is part of Efforia project.
#
# Copyright (C) 2011-2013 William Oliveira de Lagos <william@efforia.com.br>
#
# Efforia is free software: you can redistribute it and/or modify
# it under the terms of the Lesser GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Efforia is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Efforia. If not, see <http://www.gnu.org/licenses/>.
#

from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Hidden, HTML, Field

class TutorialForm(forms.Form):
    career = forms.CharField(label='',widget=forms.TextInput(attrs={'placeholder':'No que voce trabalha atualmente?'}))
    birth  = forms.CharField(label='',widget=forms.TextInput(attrs={'placeholder':'Quando voce nasceu?'}))
    bio    = forms.CharField(label='',widget=forms.Textarea(attrs={'rows':5,'placeholder':'Fale um pouco sobre voce.'}))
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_class = 'form-signin'
        self.helper.form_action = '/efforia/tutorial'
        self.helper.layout = Layout(
            Div(Field('career',css_class='form-control'),css_class='form-group'),
            Div(Field('birth',css_class='datepicker form-control'),css_class='form-group'),
            Div(Field('bio',css_class='form-control'),css_class='form-group'),
        )
        super(TutorialForm, self).__init__(*args, **kwargs)