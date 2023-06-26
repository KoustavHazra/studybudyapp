from rest_framework.decorators import api_view
from rest_framework.response import Response
from base.models import Room
from .serializers import RoomSerializer

@api_view(['GET'])
def getRoutes(request):
    routes = [
        'GET /api'
        'GET /api/rooms',
        'GET /api/rooms/:id'
    ]
    '''
    NOTE:
    the routes we're making here are used to get the data in json format. So in the second link, /api/rooms -- anyone can 
    get the room names using that api.
    For the third one anyone can get the data of any particular room by giving the room id within the url.
    '''
    return Response(routes)
    '''
    NOTE:
    In case of ---> return JsonResponse(routes, safe=False)
    the safe=False helps to turn the routes list into a json list. 
    So this json response is going to convert this data into json data.  
    '''

@api_view(['GET'])
def getRooms(request):
    rooms = Room.objects.all()
    serializer = RoomSerializer(rooms, many=True)
    '''
    NOTE:
    many=True --- means, we might need to serialize more than one number of objects, and thus we added this param.
    '''
    return Response(serializer.data)


@api_view(['GET'])
def getRoom(request, pk):
    room = Room.objects.get(id=pk)
    serializer = RoomSerializer(room, many=False)
    return Response(serializer.data)