
from django.contrib import messages
from django.contrib.auth.models import Group, User
from django.shortcuts import redirect, render,get_object_or_404
from django.contrib.auth.decorators import login_required,permission_required
from ..forms import Create_User_Form


@login_required
@permission_required('auth.add_user',login_url='/login/')
def list_users(request):
  users=User.objects.all()
  data={'users':users}
  return render(request,'users/list_users.html',data)

@login_required
@permission_required('auth.add_user',login_url='/login/')
def create_user(request):
  if request.method=="POST":
    form=Create_User_Form(request.POST)
    if form.is_valid():
      form.save()
      user = form.save()
      # adding user in to a group on user creation
      group = form.cleaned_data['group']
      user.groups.add(group)
      form = Create_User_Form()
      messages.success(request,"User created succesfully !!")
      return redirect('createuser')
  else:
    form=Create_User_Form()
  data={'form':form}
  return render(request,'users/create_user.html',data)
