from django import template

register = template.Library()

@register.filter('addstr')
def addstr(arg1, arg2):
    """
    Function to add two strings
    """
    return str(arg1) + str(arg2)

@register.filter('checkdefault')
def checkdefault(str_val, str_default='home'):
    """
    Function to use str_val if it is not the empty string, otherwise use str_default
    """
    if str_val == '':
        return str_default
    return str_val
