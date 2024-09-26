from django import template
from home.forms import UpdateWorkspaceForm,\
                    DeleteWorkspaceForm

register = template.Library()


@register.filter('addstr')
def addstr(arg1, arg2):
    """
    Function to add two strings
    """
    return str(arg1) + str(arg2)

@register.inclusion_tag(\
    'home/delete_workspace.html',\
    name='initialize_delete_workspace'\
    )
def initialize_delete_workspace(workspace, user):
    return {'form':DeleteWorkspaceForm(user=user, initial={'workspace':workspace})}

@register.inclusion_tag(\
    'home/update_workspace.html',\
    name='initialize_update_workspace'\
    )
def initialize_update_workspace(workspace, user):
    return {'as_modal':True, 'workspace':workspace, 'form':UpdateWorkspaceForm(user=user, instance=workspace, initial={'workspace':workspace})}
