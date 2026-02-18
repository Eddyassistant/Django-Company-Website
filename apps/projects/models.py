from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.blocks import CharBlock, RichTextBlock
from wagtail.fields import StreamField
from wagtail.images.blocks import ImageChooserBlock
from wagtail.models import Page


class ProjectIndexPage(Page):
    intro = models.TextField(blank=True, default="")

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
    ]

    parent_page_types = ["home.FlexPage"]
    subpage_types = ["projects.ProjectPage"]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        projects = ProjectPage.objects.live().descendant_of(self).order_by("-project_date")
        paginator = Paginator(projects, 9)
        page_number = request.GET.get("page")
        try:
            projects = paginator.page(page_number)
        except PageNotAnInteger:
            projects = paginator.page(1)
        except EmptyPage:
            projects = paginator.page(paginator.num_pages)
        context["projects"] = projects
        return context

    class Meta:
        verbose_name = "Projektoversigt"


class ProjectPage(Page):
    short_description = models.CharField(max_length=500, blank=True, default="")
    project_date = models.DateField("Projektdato")
    client = models.CharField(max_length=255, blank=True, default="")
    location = models.CharField(max_length=255, blank=True, default="")
    main_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    body = StreamField(
        [
            ("heading", CharBlock(classname="title")),
            ("paragraph", RichTextBlock()),
            ("image", ImageChooserBlock()),
            ("gallery", CharBlock(label="Galleri (brug Billedgalleri-blokken på FlexPage)")),
        ],
        blank=True,
    )

    content_panels = Page.content_panels + [
        FieldPanel("short_description"),
        FieldPanel("project_date"),
        FieldPanel("client"),
        FieldPanel("location"),
        FieldPanel("main_image"),
        FieldPanel("body"),
    ]

    parent_page_types = ["projects.ProjectIndexPage"]
    subpage_types = []

    class Meta:
        verbose_name = "Projekt"
        verbose_name_plural = "Projekter"
