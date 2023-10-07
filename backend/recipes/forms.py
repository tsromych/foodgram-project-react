from django import forms


class DeleteFildInlineFormSet(forms.BaseInlineFormSet):

    def clean(self):
        super().clean()
        count = 0
        elem_from_delete = 0
        for form in self.forms:
            if form.cleaned_data['DELETE']:
                elem_from_delete += 1
            count += 1
        if count == elem_from_delete:
            raise forms.ValidationError(
                'Должно присутствовать хотя бы одно поле'
            )
