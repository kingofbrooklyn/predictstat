from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from .forms import *
from home.forms import SelectWorkspaceForm, DeleteWorkspaceForm, UpdateWorkspaceForm

def get_home_context(request):

    context = {}
    context['page_title'] = "Account Home"

    return context


@login_required(login_url='account-login')
def home(request):

    """
    Account home view
    """

    context = get_home_context(request)

    return render(request, 'account/home.html', context)

def register(request):

    """
    Register an account
    """

    # If user is already logged in, redirect to account home
    if request.user.is_authenticated:
        return redirect('account-home')

    context = {}

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        context['form'] = form # Update in case form is invalid and errors need to be displayed to user

        if form.is_valid():
            user = form.save()
            login(request, user)

            return redirect('account-home')

    elif request.method == 'GET':
        context['form'] = RegisterForm()

    return render(request, 'account/register.html', context)

def login_(request):

    """
    Log in to an account
    """

    # If the user is already authenticated, redirect to home
    if request.user.is_authenticated:
        return redirect('account-home')

    context = {}

    if request.method == 'POST':

        form = LoginForm(request=request, data=request.POST)
        context['form'] = form # Update context with form in case form is invalid
                               # and errors need to be displayed to user

        if form.is_valid():

            # Check login credentials
            user = authenticate(\
                username=form.cleaned_data.get('username'),\
                password=form.cleaned_data.get('password')\
            )

            if user is not None:

                # Login the user
                login(request, user)

                return redirect('account-home')

    elif request.method == 'GET':
        context['form'] = LoginForm()

    return render(request, 'account/login.html', context)

@login_required(login_url='account-login')
def logout_(request):

    """
    Log out of logged-in account, redirect to home-home
    """

    logout(request)

    return redirect('account-home')


@login_required(login_url='account-login')
def delete_workspace(request):

    if request.POST:

        form = DeleteWorkspaceForm(request.POST, user=request.user)

        if form.is_valid():
            workspace = form.cleaned_data.get('workspace')
            workspace_active_id = request.session.get('workspace_active')
            if workspace_active_id and workspace_active_id == workspace.id:
                request.session.pop('workspace_active')
            workspace.delete()
            return redirect('account-home')

        context = get_home_context(request)
        context['delete_workspace_form'] = form

        return render(request, 'account/home.html', context)

    context = {'form': DeleteWorkspaceForm(user=request.user)}
    return render(request, 'account/delete_workspace.html', context)

@login_required(login_url='account-login')
def update_workspace(request):

    ### POST ###
    if request.POST:

        form = UpdateWorkspaceForm(request.POST, user=request.user)

        if form.is_valid():
            workspace_old = form.cleaned_data.get('workspace')
            workspace = form.save(commit=False)
            workspace.id = workspace_old.id
            workspace.save()
            return redirect('account-home')

        context = get_home_context(request)
        context['update_workspace_form'] = form

        return render(request, 'account/home.html', context)

    ### GET ###
    select_form = SelectWorkspaceForm(request.GET, user=request.user)
    if select_form.is_valid():
        workspace = select_form.get('workspace')
        context = {'form': UpdateWorkspaceForm(instance=workspace, user=request.user)}
        return render(request, 'account/update_workspace.html', context)
    else:
        context = {'form': select_form}
        return render(request, 'account/update_workspace.html', context)
