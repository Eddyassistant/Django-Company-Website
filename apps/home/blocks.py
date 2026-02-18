from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock


class HeroBlock(blocks.StructBlock):
    """Full-width hero banner with title, subtitle, image, CTA button."""

    title = blocks.CharBlock(required=True)
    subtitle = blocks.CharBlock(required=False)
    image = ImageChooserBlock(required=False)
    button_text = blocks.CharBlock(required=False, default="Læs mere")
    button_link = blocks.PageChooserBlock(required=False)

    class Meta:
        template = "blocks/hero_block.html"
        icon = "image"
        label = "Hero-banner"


class AboutBlock(blocks.StructBlock):
    """About section with image + text side by side."""

    heading = blocks.CharBlock(required=True)
    text = blocks.RichTextBlock(required=True)
    image = ImageChooserBlock(required=False)
    image_position = blocks.ChoiceBlock(
        choices=[
            ("left", "Venstre"),
            ("right", "Højre"),
        ],
        default="left",
    )

    class Meta:
        template = "blocks/about_block.html"
        icon = "user"
        label = "Om os"


class ServicesBlock(blocks.StructBlock):
    """Grid of service cards."""

    heading = blocks.CharBlock(required=True, default="Vores ydelser")
    services = blocks.ListBlock(
        blocks.StructBlock(
            [
                ("title", blocks.CharBlock()),
                ("description", blocks.RichTextBlock()),
                (
                    "icon",
                    blocks.CharBlock(
                        required=False,
                        help_text="Bootstrap Icon class, e.g. bi-hammer",
                    ),
                ),
            ]
        )
    )

    class Meta:
        template = "blocks/services_block.html"
        icon = "cogs"
        label = "Ydelser"


class ProjectsShowcaseBlock(blocks.StructBlock):
    """Shows latest N projects from the project index."""

    heading = blocks.CharBlock(required=True, default="Aktuelle projekter")
    projects_page = blocks.PageChooserBlock(page_type="projects.ProjectIndexPage", required=False)
    count = blocks.IntegerBlock(default=3, min_value=1, max_value=12)
    button_text = blocks.CharBlock(required=False, default="Alle projekter")

    class Meta:
        template = "blocks/projects_showcase_block.html"
        icon = "folder-open-inverse"
        label = "Projektudstilling"

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        projects_page = value.get("projects_page")
        if projects_page:
            projects_page = projects_page.specific
            try:
                from apps.projects.models import ProjectPage  # noqa: F401

                context["projects"] = (
                    projects_page.get_children()
                    .live()
                    .specific()
                    .order_by("-projectpage__project_date")[: value.get("count", 3)]
                )
                context["projects_index_url"] = projects_page.url
            except Exception:
                context["projects"] = []
                context["projects_index_url"] = "#"
        else:
            context["projects"] = []
            context["projects_index_url"] = "#"
        return context


class ContactBlock(blocks.StructBlock):
    """Contact section with heading, text, and contact details."""

    heading = blocks.CharBlock(required=True, default="Kontakt os")
    text = blocks.CharBlock(required=False)
    address = blocks.CharBlock(required=False)
    phone = blocks.CharBlock(required=False)
    email = blocks.EmailBlock(required=False)

    class Meta:
        template = "blocks/contact_block.html"
        icon = "mail"
        label = "Kontakt"


class LocationBlock(blocks.StructBlock):
    """Location/map embed block."""

    heading = blocks.CharBlock(required=True, default="Find os")
    address = blocks.CharBlock(required=True)
    map_embed = blocks.RawHTMLBlock(required=False, help_text="Google Maps embed HTML or similar")

    class Meta:
        template = "blocks/location_block.html"
        icon = "site"
        label = "Lokation / Kort"


class RichTextSection(blocks.StructBlock):
    """Generic rich text content section."""

    heading = blocks.CharBlock(required=False)
    content = blocks.RichTextBlock()
    background = blocks.ChoiceBlock(
        choices=[
            ("white", "Hvid"),
            ("light", "Lys"),
            ("dark", "Mørk"),
        ],
        default="white",
    )

    class Meta:
        template = "blocks/richtext_section_block.html"
        icon = "pilcrow"
        label = "Tekst-sektion"


class ImageGalleryBlock(blocks.StructBlock):
    """Image gallery grid."""

    heading = blocks.CharBlock(required=False)
    images = blocks.ListBlock(ImageChooserBlock())

    class Meta:
        template = "blocks/gallery_block.html"
        icon = "image"
        label = "Billedgalleri"


class CTABlock(blocks.StructBlock):
    """Call to action banner."""

    heading = blocks.CharBlock(required=True)
    text = blocks.CharBlock(required=False)
    button_text = blocks.CharBlock(required=True)
    button_link = blocks.PageChooserBlock(required=False)
    button_url = blocks.URLBlock(
        required=False,
        help_text="External URL (bruges hvis ingen side er valgt)",
    )
    background = blocks.ChoiceBlock(
        choices=[
            ("primary", "Primær"),
            ("dark", "Mørk"),
            ("light", "Lys"),
        ],
        default="primary",
    )

    class Meta:
        template = "blocks/cta_block.html"
        icon = "pick"
        label = "Call to Action"


class TestimonialsBlock(blocks.StructBlock):
    """Customer testimonials/quotes."""

    heading = blocks.CharBlock(required=False, default="Hvad vores kunder siger")
    testimonials = blocks.ListBlock(
        blocks.StructBlock(
            [
                ("quote", blocks.TextBlock()),
                ("author", blocks.CharBlock()),
                (
                    "role",
                    blocks.CharBlock(
                        required=False,
                        help_text="e.g. 'Privatkunde' or 'Virksomhed'",
                    ),
                ),
            ]
        )
    )

    class Meta:
        template = "blocks/testimonials_block.html"
        icon = "openquote"
        label = "Anmeldelser"


class SpacerBlock(blocks.StructBlock):
    """Vertical spacing."""

    height = blocks.ChoiceBlock(
        choices=[
            ("small", "Lille (2rem)"),
            ("medium", "Medium (4rem)"),
            ("large", "Stor (8rem)"),
        ],
        default="medium",
    )

    class Meta:
        template = "blocks/spacer_block.html"
        icon = "arrows-up-down"
        label = "Mellemrum"
