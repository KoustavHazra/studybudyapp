from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    name = models.CharField(max_length=200, null=True)
    username = models.CharField(max_length=50, null=False, unique=True)
    email = models.EmailField(unique=True, null=True)
    #  unique=True --- helps us to get unique values, so that two different user doesn't have the same email id.
    #  we can do this for username as well. So that it shows " Username is already taken. "
    bio = models.TextField(null=True, blank=True)
    avatar = models.ImageField(null=True, default="avatar.svg")
    USERNAME_FIELD = 'email'  
    # this will now set the email as username, so while logging in we need the email and not the username.
    REQUIRED_FIELDS = []

class Topic(models.Model):
    # this is the parent of Room class
    name = models.CharField(max_length=200)
    
    def __str__(self) -> str:
        return self.name

class Room(models.Model):
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)
    '''
    NOTE:
    a topic can have multiple rooms, but a room will only have a single topic.
    if a topic is deleted, we want it to be null. Thus we've used models.SET_NULL.
    So while using models.SET_NULL, we need to add the null=True in code so that the db allows it.
    '''
    
    '''
    NOTE: 
    As we've added the Topic class code above this Room class, we added the Topic name in the .ForeignKey() method
    without any quotes. 
    If we had written the same Topic class code beneath the Room class, we had to quote the
    Topic inside the .ForeignKey() method.
    '''

    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    # null = True means, it can be left blank while creating the database.
    # blank = True, means it can be left blank while filling up the form.
    
    participants = models.ManyToManyField(User, related_name='participants', blank=True)

    updated = models.DateTimeField(auto_now=True)  # this will take a snap of the time whenever this model/table was updated.
    # auto_now = True, means it will automatically take the snaps of time and we don't need to do anything manually.

    created = models.DateTimeField(auto_now_add=True)
    # auto_now_add = True, it will only take a snap of time when we first save or create this instance. 
    # It'll never change if we save the instance multiple times, while the autp_save will change.

    class Meta:
        ordering = ['-updated', '-created']

    def __str__(self):
        return self.name

class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    '''
    NOTE:
    here we've created a one=to-many relationship. Where a single Room can have multiple messages.
    For that we need to use this .ForeignKey() method to specify, that Room is the parent model, and
    this mdoel, Message, will show its messages.
    on_delete = models.CASCADE, means that all the messages will be deleted if the parent class(Room) has
    been deleted.
    '''

    body = models.TextField()
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-updated', '-created']
        
    '''
    NOTE:
    when we're adding values, we want to see the newest one as the first one. And for that we made this class.
    we're ordering them by specifying the updated and created in the list. And based on the first item of the list
    ordering will be prioritized. So if we want to see the oldest one as first, we can keep created as first element.
    
    In the list we've wrote them names with a '-' in front of them.. it makes the order reverse.
    '''

    def __str__(self):
        return self.body[0:50]