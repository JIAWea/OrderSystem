from django.forms import ModelForm
from backend.models import BackendUser


class BackendUserForm(ModelForm):
    class Meta:
        model = BackendUser
        fields = '__all__'
