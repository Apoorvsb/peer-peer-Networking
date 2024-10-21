from django.shortcuts import render,redirect
from django.db.models import Q
from .models import Room, Topic ,Message,User
from .forms import RoomForm,UserForm
from django.http import HttpResponse

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from .forms import RoomForm, UserForm, MyUserCreationForm


# Create your views here.
# rooms=[{'id':1 ,'name':'lets learn django'},{'id':2,'name':'learning pythin is fun'},{'id':3,'name':'coding is not alwats fun'}


def home(request):
    q=request.GET.get('q') if request.GET.get('q')!=None else ''
    rooms=Room.objects.filter(Q(topic__name__icontains=q) | Q(name__icontains=q) | Q(description__icontains=q) | Q(host__username=q))
    topics=Topic.objects.all()[0:5]
    room_count=rooms.count()
    room_messages=Message.objects.filter(Q(room__topic__name__icontains=q))
    

    context={'rooms':rooms,'topics':topics,'room_count':room_count,'room_messages':room_messages}

    return render(request,'base/home.html',context)


def loginPage(request):
    page='login'
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method=='POST':
        username=request.POST.get('username').lower()
        password=request.POST.get('password')
        try:
            user=User.objects.GET(username=username)
        except:
            messages.error(request,"user doesnot exists")  #done mannually means without using builtin
                                                                 # funcions look it up properly
        user=authenticate(request,username=username,password=password)
        if user is not None:
            login(request,user)
            return redirect('home')
        else:
            messages.error(request,'user does not exists')    
    context={'page':page}
    return render(request,'base/login_register.html',context)  


def registerUser(request):
    form = MyUserCreationForm()

    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'An error occurred during registration')

    return render(request, 'base/login_register.html', {'form': form})   


    return render(request,'base/login_register.html',{'form':form})

def logoutUser(request):
    logout(request)
    return redirect('home')


def room(request,ptr):
    
    rooms=Room.objects.get(id=ptr)
    room_messages=rooms.message_set.all()
    
    participants=rooms.participants.all()
    # for i in rooms:
    #     if i['id']==int(ptr):
    #         room=i
    if request.method=='POST':  #this is the method we can use instead of save() basic way of saving insread of save
        message=Message.objects.create(
            room=rooms,
            user=request.user,
            body=request.POST.get('body')
            )
        rooms.participants.add(request.user)    
        return redirect('room',ptr=rooms.id)
        
    
    context={'rooms':rooms,'room_messages':room_messages ,'participants':participants}        
    return render(request,'base/room.html',context)

def userprofile(request,ptr):
    user=User.objects.get(id=ptr)
    rooms=user.room_set.all() #here the room_set means room is the module set.all() is used to take all the room of user
    room_messages=user.message_set.all()
    topics=Topic.objects.all()
    context={'user':user ,'rooms':rooms,'room_messages':room_messages,'topics':topics}
    
    return render(request,'base/profile.html',context)


@login_required(login_url='login')  # restricting the user who are not logged in from creating a room
def createRoom(request):
    form=RoomForm()
    topics=Topic.objects.all()
    rooms=Room.objects.all()
    if request.method=='POST':
        topic_name=request.POST.get('topic')
        topic,created=Topic.objects.get_or_create(name=topic_name)
        Room.objects.create(
           host=request.user,
           topic=topic,
           name=request.POST.get('name'),
           description=request.POST.get('description')

        )
       #form=RoomForm(request.POST)
        #if form.is_valid():
            # form.save() #this method save here saves the data in the database
           # room=form.save(commit=False)
           # room.host=request.user
           # room.save()-->
        return redirect('home')
            
    context={'form':form ,'topics':topics , 'rooms':rooms}
    return render(request,'base/room_form.html',context)


@login_required(login_url='login')
def updateRoom(request,pk):
    room=Room.objects.get(id=pk)
    topics=Topic.objects.all()
    form=RoomForm(instance=room)
    
    if request.user != room.host:
        return HttpResponse('your are not allowed here')
    
    if request.method=='POST':
        topic_name=request.POST.get('topic')
        topic,created=Topic.objects.get_or_create(name=topic_name) 
        room.topic=topic
        room.name=request.POST.get('name')
        room.description=request.POST.get('description')
        room.save()
        #form=RoomForm(request.POST,instance=room)
        #if form.is_valid():
            #form.save() #this method save here saves the data in the database
        return redirect('home')

    context={'form':form ,'topics':topics}
    return render(request,'base/room_form.html',context)


@login_required(login_url='login')  #restricting the user who are  not logged in from deleting the room
def deleteRoom(request,pk):
    room=Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse('your are not allowed here')

    if request.method=='POST':
        room.delete()
        return redirect('home')
    return render(request,'base/delete.html',{'obj':room})   


@login_required(login_url='login')  #restricting the user who are  not logged in from deleting the room
def deleteMessage(request,pk):
    message=Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse('your are not allowed here')

    if request.method=='POST':
        message.delete()
        return redirect('home')
    return render(request,'base/delete.html',{'obj':message})   

@login_required(login_url='login')
def updateuser(request):
    user=request.user
    form=UserForm(instance=user)
    if request.method =='POST':
        
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile',ptr=user.id)
    return render(request,'base/update-user.html' ,{'form':form})
def topicspage(request):
    q = request.GET.get('q') if request.GET.get('q') is not None else ''
    topics = Topic.objects.filter(name__icontains=q)  # Use variable q instead of 'q'
    return render(request, 'base/topics.html', {'topics': topics})

def activitypage(request):
    room_messages=Message.objects.all()
    return render(request,'base/activity.html',{'room_messages':room_messages})
