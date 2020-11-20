from django import template
    
    
register= template.Library()
@register.filter
def uglify(value):
    x = [value]
    for x in value:
        if x % 2 == 0:
            return value.upper()
        else:
            return value.lower()     