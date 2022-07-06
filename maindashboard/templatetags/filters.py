from django import template

register = template.Library()


@register.filter
def has_access(user, p):
    if user.is_superuser:
        return True
    return user.user_permissions.filter(name=p).first() != None
