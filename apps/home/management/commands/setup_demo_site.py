import datetime
import json
from pathlib import Path

from django.apps import apps
from django.core.files import File
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Sets up the demo site with sample content"

    def handle(self, *args, **options):
        Page = apps.get_model("wagtailcore", "Page")
        Site = apps.get_model("wagtailcore", "Site")
        FlexPage = apps.get_model("home", "FlexPage")
        ProjectIndexPage = apps.get_model("projects", "ProjectIndexPage")
        ProjectPage = apps.get_model("projects", "ProjectPage")
        WagtailImage = apps.get_model("wagtailimages", "Image")
        SiteSettings = apps.get_model("home", "SiteSettings")

        # Fix tree structure first to avoid treebeard issues
        Page.fix_tree()
        self.stdout.write("Fixed tree structure")

        # Check if already set up
        if FlexPage.objects.exists():
            self.stdout.write(self.style.WARNING("Demo site already exists. Skipping."))
            return

        root_page = Page.objects.get(depth=1)

        # Delete default Wagtail welcome page if it exists
        for child in root_page.get_children():
            child.delete()

        # Fix tree again after deletion
        Page.fix_tree()
        root_page.refresh_from_db()

        # Load images from media/original_images/
        base_dir = Path(__file__).resolve().parent.parent.parent.parent.parent
        media_dir = base_dir / "media" / "original_images"

        image_files = {
            "woodworking-workshop.jpg": "Værksted overblik",
            "wooden-kitchen.jpg": "Trækøkken massivtræ",
            "antique-furniture.jpg": "Antikke møbler",
            "custom-cabinet.jpg": "Skræddersyet skab",
            "workshop-tools.jpg": "Værktøj og håndværk",
            "wooden-table.jpg": "Massivtræbord",
            "restoration.jpg": "Restaureringsarbejde",
            "office-furniture.jpg": "Kontorindretning",
        }

        wagtail_images = {}
        for filename, title in image_files.items():
            file_path = media_dir / filename
            if file_path.exists():
                try:
                    img = WagtailImage(title=title)
                    with open(file_path, "rb") as f:
                        img.file.save(filename, File(f), save=True)
                    wagtail_images[filename] = img
                    self.stdout.write(f"Loaded image: {title}")
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"Could not load image {filename}: {e}"))
            else:
                self.stdout.write(self.style.WARNING(f"Image not found: {file_path}"))

        # ------------------------------------------------------------------ #
        # Build the body StreamField JSON for the FlexPage                    #
        # ------------------------------------------------------------------ #
        hero_image_id = None
        if "woodworking-workshop.jpg" in wagtail_images:
            hero_image_id = wagtail_images["woodworking-workshop.jpg"].pk

        about_image_id = None
        if "wooden-kitchen.jpg" in wagtail_images:
            about_image_id = wagtail_images["wooden-kitchen.jpg"].pk

        body_data = [
            # Hero
            {
                "type": "hero",
                "id": "hero-1",
                "value": {
                    "title": "Snedkeri Meier",
                    "subtitle": "Traditionelt håndværk med passion siden 1985",
                    "image": hero_image_id,
                    "button_text": "Vores projekter",
                    "button_link": None,
                },
            },
            # About
            {
                "type": "about",
                "id": "about-1",
                "value": {
                    "heading": "Om os",
                    "text": (
                        "<p>I over 35 år har vi i vores værksted i København fremstillet "
                        "skræddersyede møbler og indretninger af træ i højeste kvalitet. "
                        "Vores erfarne team forener traditionelt håndværk med moderne "
                        "teknik for at realisere dine individuelle ønsker.</p>"
                    ),
                    "image": about_image_id,
                    "image_position": "left",
                },
            },
            # Services
            {
                "type": "services",
                "id": "services-1",
                "value": {
                    "heading": "Vores ydelser",
                    "services": [
                        {
                            "title": "Specialmøbler",
                            "description": "<p>Individuelle møbler fremstillet efter dine ønsker.</p>",
                            "icon": "bi-box",
                        },
                        {
                            "title": "Køkkener",
                            "description": "<p>Drømmekøkkener i massivtræ, perfekt planlagt og monteret.</p>",
                            "icon": "bi-house",
                        },
                        {
                            "title": "Restaurering",
                            "description": "<p>Faglig restaurering af antikke møbler.</p>",
                            "icon": "bi-clock-history",
                        },
                    ],
                },
            },
            # Projects showcase – button_link will be set later via DB update
            {
                "type": "projects_showcase",
                "id": "projects-1",
                "value": {
                    "heading": "Aktuelle projekter",
                    "projects_page": None,
                    "count": 3,
                    "button_text": "Alle projekter",
                },
            },
            # Contact
            {
                "type": "contact",
                "id": "contact-1",
                "value": {
                    "heading": "Kontakt os",
                    "text": "Har du et projekt i tankerne? Vi rådgiver dig gerne!",
                    "address": "Bredgade 42, 1260 København K",
                    "phone": "+45 33 12 34 56",
                    "email": "info@snedkeri-meier.dk",
                },
            },
        ]

        # Create FlexPage (blank body first, then update via JSON)
        home = FlexPage(
            title="Snedkeri Meier",
            slug="home",
        )
        root_page.add_child(instance=home)
        FlexPage.objects.filter(pk=home.pk).update(body=json.dumps(body_data))
        home.refresh_from_db()
        self.stdout.write(self.style.SUCCESS("Created FlexPage (home)"))

        # ------------------------------------------------------------------ #
        # ProjectIndexPage                                                     #
        # ------------------------------------------------------------------ #
        project_index = ProjectIndexPage(
            title="Projekter",
            slug="projekter",
            show_in_menus=True,
            intro="Udforsk vores afsluttede projekter og lad dig inspirere.",
        )
        home.add_child(instance=project_index)
        self.stdout.write(self.style.SUCCESS("Created ProjectIndexPage"))

        # Update projects_showcase block to point at ProjectIndexPage
        for block in body_data:
            if block["type"] == "projects_showcase":
                block["value"]["projects_page"] = project_index.pk
        FlexPage.objects.filter(pk=home.pk).update(body=json.dumps(body_data))
        home.refresh_from_db()
        self.stdout.write("Updated projects_showcase to reference ProjectIndexPage")

        # ------------------------------------------------------------------ #
        # Sample projects                                                      #
        # ------------------------------------------------------------------ #
        projects_data = [
            {
                "title": "Egetræskøkken Familie Hansen",
                "slug": "egetraeskokken-hansen",
                "short_description": ("Skræddersyet køkken i massiv eg med moderne udstyr og traditionelt håndværk."),
                "project_date": datetime.date(2024, 3, 15),
                "client": "Familie Hansen",
                "location": "København Ø",
                "image_key": "wooden-kitchen.jpg",
            },
            {
                "title": "Kontorindretning Advokatfirma Weber",
                "slug": "kontor-advokatfirma-weber",
                "short_description": (
                    "Komplet kontorindretning i valnøddetræ til et anerkendt advokatfirma i Københavns indre by."
                ),
                "project_date": datetime.date(2024, 6, 20),
                "client": "Advokatfirma Weber & Partners",
                "location": "København K",
                "image_key": "office-furniture.jpg",
            },
            {
                "title": "Restaurering af barokskab",
                "slug": "restaurering-barokskab",
                "short_description": (
                    "Omfattende restaurering af et barokskab fra det 18. århundrede med originale teknikker."
                ),
                "project_date": datetime.date(2024, 9, 10),
                "client": "Privatsamler",
                "location": "København",
                "image_key": "restoration.jpg",
            },
        ]

        for data in projects_data:
            image_key = data.pop("image_key", None)
            project = ProjectPage(**data)
            if image_key and image_key in wagtail_images:
                project.main_image = wagtail_images[image_key]
            project_index.add_child(instance=project)
            self.stdout.write(self.style.SUCCESS(f"Created ProjectPage: {data['title']}"))

        # ------------------------------------------------------------------ #
        # Wagtail Site + SiteSettings                                         #
        # ------------------------------------------------------------------ #
        Site.objects.all().delete()
        site = Site.objects.create(
            hostname="localhost",
            port=8000,
            root_page=home,
            is_default_site=True,
            site_name="Snedkeri Meier",
        )
        self.stdout.write(self.style.SUCCESS("Created default Site"))

        SiteSettings.objects.update_or_create(
            site=site,
            defaults={
                "site_name": "Snedkeri Meier",
                "tagline": "Traditionelt håndværk med moderne teknik.",
                "opening_hours": "Man - Fre: 7:00 - 17:00\nLør: 8:00 - 12:00\nSøn: Lukket",
                "footer_text": "",
                "address": "Bredgade 42, 1260 København K",
                "phone": "+45 33 12 34 56",
                "email": "info@snedkeri-meier.dk",
            },
        )
        self.stdout.write(self.style.SUCCESS("Created SiteSettings"))

        self.stdout.write(self.style.SUCCESS("\nDemo site setup complete!"))
