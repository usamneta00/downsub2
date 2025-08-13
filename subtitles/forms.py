from django import forms


class URLForm(forms.Form):
    url = forms.URLField(
        label='',
        widget=forms.TextInput(
            attrs={
                'class': 'url-input',
                'placeholder': 'أدخل رابط YouTube هنا...',
                'id': 'url-input'
            }
        ),
    )