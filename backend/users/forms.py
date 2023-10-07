from django import forms

from .models import Subscription


class SubscribeForm(forms.ModelForm):

    class Meta:
        model = Subscription
        fields = (
            'user',
            'author'
        )

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('user') == cleaned_data.get('author'):
            raise forms.ValidationError(
                'Автором не может быть сам подписчик'
            )
        return cleaned_data
