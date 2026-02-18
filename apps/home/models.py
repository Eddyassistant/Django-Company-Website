from django.db import models
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.fields import StreamField
from wagtail.models import Page

from .blocks import (
    AboutBlock,
    ContactBlock,
    CTABlock,
    HeroBlock,
    ImageGalleryBlock,
    LocationBlock,
    ProjectsShowcaseBlock,
    RichTextSection,
    ServicesBlock,
    SpacerBlock,
    TestimonialsBlock,
)


@register_setting
class SiteSettings(BaseSiteSetting):
    site_name = models.CharField(
        max_length=255,
        default="Snedkeri Meier",
        help_text="Virksomhedens navn (vises i navbar, footer og titel)",
    )
    tagline = models.CharField(
        max_length=500,
        default="Traditionelt håndværk med moderne teknik.",
        help_text="Sloganet der vises i footeren",
    )
    opening_hours = models.TextField(
        blank=True,
        default="Man - Fre: 7:00 - 17:00\nLør: 8:00 - 12:00\nSøn: Lukket",
        help_text="Åbningstider (ét linje per tidspunkt)",
    )
    footer_text = models.CharField(
        max_length=500,
        blank=True,
        default="",
        help_text="Valgfri copyright-tekst i footeren. Tom = autogenereret.",
    )
    address = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text="Virksomhedens adresse (vises i footer)",
    )
    phone = models.CharField(
        max_length=50,
        blank=True,
        default="",
        help_text="Telefonnummer (vises i footer)",
    )
    email = models.EmailField(
        blank=True,
        default="",
        help_text="E-mail (vises i footer)",
    )

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("site_name"),
                FieldPanel("tagline"),
                FieldPanel("opening_hours"),
                FieldPanel("footer_text"),
            ],
            heading="Generelt",
        ),
        MultiFieldPanel(
            [
                FieldPanel("address"),
                FieldPanel("phone"),
                FieldPanel("email"),
            ],
            heading="Kontaktoplysninger (footer)",
        ),
    ]

    def __str__(self) -> str:
        return self.site_name

    class Meta:
        verbose_name = "Indstillinger"


class FlexPage(Page):
    """Flexible page that can be assembled from reusable components."""

    body = StreamField(
        [
            ("hero", HeroBlock()),
            ("about", AboutBlock()),
            ("services", ServicesBlock()),
            ("projects_showcase", ProjectsShowcaseBlock()),
            ("contact", ContactBlock()),
            ("location", LocationBlock()),
            ("richtext", RichTextSection()),
            ("gallery", ImageGalleryBlock()),
            ("cta", CTABlock()),
            ("testimonials", TestimonialsBlock()),
            ("spacer", SpacerBlock()),
        ],
        blank=True,
    )

    content_panels = Page.content_panels + [
        FieldPanel("body"),
    ]

    # Can be placed at the very top of the tree or under another FlexPage
    parent_page_types = ["wagtailcore.Page", "home.FlexPage"]
    subpage_types = ["home.FlexPage", "projects.ProjectIndexPage"]

    class Meta:
        verbose_name = "Fleksibel side"
        verbose_name_plural = "Fleksible sider"
