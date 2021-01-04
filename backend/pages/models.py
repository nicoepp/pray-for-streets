from django.db import models

from wagtail.core.models import Page
from wagtail.core.fields import StreamField
from wagtail.core import blocks
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel


class HomePage(Page):
    body = StreamField([
        ('title', blocks.CharBlock(form_classname='title', required=False)),
        ('paragraph', blocks.TextBlock(form_classname='full')),
    ])

    content_panels = Page.content_panels + [
        StreamFieldPanel('body'),
    ]
