from django.forms import ModelForm
from .models import Room, User
from django.contrib.auth.forms import UserCreationForm

class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['name', 'username', 'email', 'password1', 'password2']


class RoomForm(ModelForm):  # a form for the room. thus named RoomForm.
    # we atleast need to values.
    class Meta:
        model = Room
        fields = '__all__'  
        # this "__all__" value will create the form based on the metadata of the Room. 
        # So all the fields we've in Room, will be added here.
        # we can also specifically mention the fields which we want to add, and we can do that by
        # adding them in a list and passing as, fields = ['name', 'date']

        exclude = ['host', 'participants']
        '''
        NOTE:
        while creating a room, we didn't wanted to select host or participants, as for host
        since we're already logged in, it'll be more logical that the host is automatically selected as us.
        Thus we excluded "host" from the form field.
        Also for participants, we didn't wanted to select any particular participants in our room, thus we excluded that
        as well.

        And obviously, these fields we just removed are for the front-end only. 
        For backend, we need to change in views ofcourse - so that those excluded values changed as per our need.
        '''

class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['avatar', 'name', 'username', 'email', 'bio']