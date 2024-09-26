from django import template

register = template.Library()

@register.filter('addstr')
def addstr(arg1, arg2):
    """
    Function to add two strings
    """
    return str(arg1) + str(arg2)
