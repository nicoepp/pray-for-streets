from django.db import models

from wagtail.core.models import Page
from wagtail.core.fields import StreamField
from wagtail.core import blocks
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.images.blocks import ImageChooserBlock

RICHTEXT_FEATURES = ['h2', 'h3', 'h4', 'ul', 'ol', 'bold', 'italic', 'link', 'hr']


class HomePage(Page):
    body = StreamField([
        ('title', blocks.CharBlock(form_classname='title', required=False)),
        ('paragraph', blocks.TextBlock(form_classname='full')),
        ('rich', blocks.RichTextBlock(form_classname='full', features=RICHTEXT_FEATURES)),
    ])

    content_panels = Page.content_panels + [
        StreamFieldPanel('body'),
    ]

    parent_page_types = [Page]


class SubPage(Page):
    body = StreamField([
        ('title', blocks.CharBlock(form_classname='title', icon='title')),
        ('paragraph', blocks.TextBlock(form_classname='full')),
        ('rich', blocks.RichTextBlock(form_classname='full', features=RICHTEXT_FEATURES)),
        ('images', blocks.StreamBlock(
            [
                ('image', ImageChooserBlock()),
            ],
            icon='image'
        )),
    ])

    content_panels = Page.content_panels + [
        StreamFieldPanel('body'),
    ]

    parent_page_types = ['pages.HomePage']
    subpage_types = []
