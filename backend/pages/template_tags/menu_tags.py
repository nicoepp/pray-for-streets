from django import template
from django.template.defaultfilters import stringfilter
from wagtail.core.models import Page

register = template.Library()


@register.simple_tag()
def get_menu(page: Page):
    return page.get_children().live().in_menu().specific()


@register.filter()
@stringfilter
def split(value: str, arg):
    return value.split(arg)
