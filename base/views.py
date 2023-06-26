from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Room, Topic, Message, User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import RoomForm, UserForm, MyUserCreationForm


# Create your views here.

def loginPage(request):
    page = 'login'

    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == "POST":
        email = request.POST.get('email').lower()
        password = request.POST.get('password')
        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request, "User does not exists.")
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Username or Password does not exists.")
    context = {"page": page}
    return render(request, 'base/login_register.html', context)

def logoutUser(request):
    logout(request)
    return redirect('home')

def registerPage(request):
    page = 'register'
    form = MyUserCreationForm()
    if request.method == "POST":
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            '''
            NOTE:
            by doing form.save(), we're saving the form and freezing it in time because we want to be able to access the user
            that was created. And to do that, we had to add commit=False, so that we can get the user object.

            The reason why we want to do that is if for some reason the user created thier username with some uppercase letters,
            we will be able to save it as a lowercase one.
            '''
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            try:
                user = User.objects.get(username=form.data.get('username'))
                messages.error(request, 'username is already taken.')
            except User.DoesNotExist:
                messages.error(request, 'Password must contain upper-lowercase, numbers and special chars.')
                
    return render(request, 'base/login_register.html', {'form': form})


# @login_required(login_url="login")
def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    '''
    NOTE:
    q = request.GET.get('q') --- this part is to get whatever is passed through  the link.
    now if we only keep this, then while "All" filter is used, none of the rooms will be shown as every room has their specifig tag.
    That's why we added this if-else statement "if request.GET.get('q') != None else ''" --- so that if the filter is "All"
    then all of the rooms will be shown, otherwise based on the filter rooms will be shown.

    Also while using the filter() we gave the argument name as, "topic__name__icontains" === where the __icontains part helps us 
    to do a case insensitive search for all records that have the value "Py" in the lastname column, where q = Py.
    So if we have searched like writing only "Py" instead of full "Python", then based on the search it'll match whatever is the closesest
    match to it and show that to us.

    NOTE:
    The "icontains" lookup is used to get records that contains a specified value.

    The "icontains" lookup is case insensitive.

    For a case sensitive search, use the "contains" lookup.
    '''
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains = q) |
        Q(description__icontains = q)
        )
    '''
    NOTE:
    Q() --- this is also a lookup method in django like __icontains.
    Let's say we don't want to search through the topic, instead we want to search with the name,
    then we cannot do that.
    That's why to make the search/filter more dynamic we use the Q() to filter with whaterver value we pass.
    And thus while using Q() we can either use it with multiple filters separately by using "or" 
    or we can use "and" to use multiple filters at once.
    '''
    room_count = rooms.count()
    topics = Topic.objects.all()[0:5]
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))
    '''
    NOTE:
    Here by doing "Message.objects.all()" --- we're getting all the messages, but we can also use filter here
    to show only our friends messages/ comments. We can do it by using a filter() method.

    UPDATE:
    now the all() is changed to filter() method with the Q-lookup method, which makes it filter the feed based upon the topics
    we choose form the topics bar.

    However we can also filter it to show our friends' messages only.
    '''
    context = {'rooms': rooms, 'topics': topics, "room_count": room_count,
                "room_messages": room_messages}
    return render(request, 'base/home.html', context)


@login_required(login_url="login")
def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all()
    '''
    NOTE:
    message_set.all() --- in django, we can query child objects from a child model. So here the parent class is the Room model
    and Message model is child class, and while querying from a child class, we put the class name in lower(message/ not Message).
    And message_set.all() means, give us all the set of messages related to this room.

    '''
    participants = room.participants.all()
    if request.method == 'POST':
        message = Message.objects.create(
            user = request.user,
            room = room,
            body = request.POST.get('body')  
            # the body is geeting whatever is passed in the form of room.html, class=comment-form. The name='body' is used here, to get the data.
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)
        '''
        NOTE:
        This return above we wrote, was kinda not necessary as anyway after commenting the user will stay on the same page only
        and the page will refresh as well.
        But as while commenting the request will be a POST request, this might mess up some functionality. That's why if we added that
        return statement, as then the page will be fully reloaded and we'll get back with a GET request and not a POST request.
        '''
    context = {'room': room, 'room_messages': room_messages, 'participants': participants}
    return render(request, 'base/room.html', context)


@login_required(login_url="login")
def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    # here we've kept the variable name "rooms" because in the feed_component we're using this same variable as "rooms".
    # so that it doesn't have issue with other components, we have kept the name same.
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {"user": user, "rooms": rooms, 
               "room_messages": room_messages, "topics": topics}
    return render(request, 'base/profile.html', context)


'''
NOTE:
This part "@login_required(login_url="login")" --- is called a decorator, which here we're using for
restricting any user if they are not logged in to see any data like rooms, or ability to create/ delete a room.
'''
@login_required(login_url="login")
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        # form = RoomForm(request.POST)
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        '''
        NOTE:
        get_or_created() --- 
        '''
        Room.objects.create(
            host= request.user,
            topic= topic,
            name= request.POST.get('name'),
            description= request.POST.get('description'),
        )
        return redirect('home')
    
        # if form.is_valid:
        #     room = form.save(commit=False)
        #     # this commit=False gives us an instance of our room, so that we can modify the information as per our need and then save it.
        #     room.host = request.user
        #     '''
        #     NOTE:
        #     As we changed the form while creating a room that the host should automatically get selected, we have added this above step.
        #     At first, we saved the instance of the room, then we asssigned the hsot of the room as the current logged in user.
        #     and then we're saving the room and create it.
        #     '''
        #     room.save()
        

    context = {'form': form, "topics": topics}
    return render(request, 'base/room_form.html', context)


@login_required(login_url="login")
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    '''
    NOTE:
    If we know a room's id then we may login and update that room, even though that room's creator is not us.
    To restrict that this below functionality we've added.
    If the user logged in is not the same as the room-host, then they'll be not allowed to change anything.
    '''
    topics = Topic.objects.all()
    if request.user != room.host:
        return HttpResponse('You are not allowed here!!')
    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')
        
    context = {'form': form, "topics": topics, 'room': room}
    return render(request, 'base/room_form.html', context)


@login_required(login_url="login")
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    '''
    NOTE:
    If we know a room's id then we may login and delete that room, even though that room's creator is not us.
    To restrict that this below functionality we've added.
    If the user logged in is not the same as the room-host, then they'll be not allowed to delete the room.
    '''
    if request.user != room.host:
        return HttpResponse('You are not allowed here!!')
    
    if request.method == "POST":
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': room})


@login_required(login_url="login")
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)
    
    if request.user != message.user:
        return HttpResponse("You are not allowed to delete this message!")
    
    if request.method == "POST":
        message.delete()
        return redirect('home')
    
    return render(request, 'base/delete.html', {'obj': message})

# @login_required(login_url="login")
# def editMessage(request, pk):
#     # need to update to edit a message
#     room = Room.objects.get(id=pk)
#     form = RoomForm(instance=room)
    
#     '''
#     NOTE:
#     If we know a room's id then we may login and update that room, even though that room's creator is not us.
#     To restrict that this below functionality we've added.
#     If the user logged in is not the same as the room-host, then they'll be not allowed to change anything.
#     '''
#     if request.user != room.host:
#         return HttpResponse('You are not allowed here!!')
#     if request.method == 'POST':
#         form = RoomForm(request.POST, instance=room)
#         if form.is_valid:
#             form.save()
#             return redirect('home')
        
#     context = {'form': form}
#     return render(request, 'base/room_form.html', context)


@login_required(login_url="login")
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)
    if request.method == "POST":
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)
    return render(request, 'base/update-user.html', {'form': form})

@login_required(login_url="login")
def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=q)
    context = {"topics": topics}
    return render(request, 'base/topics.html', context)

@login_required(login_url="login")
def activityPage(request):
    room_messages = Message.objects.all()
    context = {}
    return render(request, 'base/activity.html', context)