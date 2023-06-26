'''
NOTE:

Sometimes in Django we'll see this error --- object of type {a particular value} is not serializable.
So what happens is we were making a query to get some python list of objects, and in python the objects cannot
be converted automatically in json format. Thus we are getting this issue.

And for that we use this serializers.py file which have some classes which will take a certain model/ object that we
want to serialize and turn it into a json formatted data.
'''

from rest_framework.serializers import ModelSerializer
from base.models import Room

class RoomSerializer(ModelSerializer):
    class Meta:
        model = Room
        fields = "__all__"
        '''
        NOTE:
        In such classes, we always need to set atleast two values. The model and fields.
        so it is taking the all the values in the class Room ( like host, topic, description, name )
        and return all of them ( as we've set the fields = "__all__" ).
        
        '''