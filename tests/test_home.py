import json

import pytest
from wagtail.test.utils import WagtailPageTestCase

from apps.home.models import FlexPage, SiteSettings


@pytest.mark.django_db
class TestFlexPage:
    def test_can_create_flex_page(self, home_page):
        assert home_page is not None
        assert home_page.title == "Test Home"

    def test_flex_page_renders(self, client, site, home_page):
        response = client.get(home_page.url)
        assert response.status_code == 200

    def test_correct_template(self, client, site, home_page):
        response = client.get(home_page.url)
        assert "home/flex_page.html" in [t.name for t in response.templates]

    def test_empty_body_renders(self, client, site, home_page):
        """FlexPage with empty body should still render without errors."""
        response = client.get(home_page.url)
        assert response.status_code == 200

    def test_hero_block_renders(self, client, site, home_page):
        """Hero block should appear when added to FlexPage body."""
        body_data = [
            {
                "type": "hero",
                "id": "hero-1",
                "value": {
                    "title": "Test Hero Title",
                    "subtitle": "Test subtitle",
                    "image": None,
                    "button_text": "Klik her",
                    "button_link": None,
                },
            }
        ]
        FlexPage.objects.filter(pk=home_page.pk).update(body=json.dumps(body_data))
        home_page.refresh_from_db()
        response = client.get(home_page.url)
        assert response.status_code == 200
        content = response.content.decode()
        assert "Test Hero Title" in content
        assert "Test subtitle" in content

    def test_about_block_renders(self, client, site, home_page):
        """About block should render heading and text."""
        body_data = [
            {
                "type": "about",
                "id": "about-1",
                "value": {
                    "heading": "Om vores virksomhed",
                    "text": "<p>Vi er en god virksomhed.</p>",
                    "image": None,
                    "image_position": "left",
                },
            }
        ]
        FlexPage.objects.filter(pk=home_page.pk).update(body=json.dumps(body_data))
        home_page.refresh_from_db()
        response = client.get(home_page.url)
        assert response.status_code == 200
        content = response.content.decode()
        assert "Om vores virksomhed" in content

    def test_services_block_renders(self, client, site, home_page):
        """Services block should render heading and service cards."""
        body_data = [
            {
                "type": "services",
                "id": "services-1",
                "value": {
                    "heading": "Vores ydelser",
                    "services": [
                        {
                            "title": "Specialmøbler",
                            "description": "<p>Møbler på mål.</p>",
                            "icon": "bi-box",
                        }
                    ],
                },
            }
        ]
        FlexPage.objects.filter(pk=home_page.pk).update(body=json.dumps(body_data))
        home_page.refresh_from_db()
        response = client.get(home_page.url)
        assert response.status_code == 200
        content = response.content.decode()
        assert "Vores ydelser" in content
        assert "Specialmøbler" in content

    def test_contact_block_renders(self, client, site, home_page):
        """Contact block should render heading and contact details."""
        body_data = [
            {
                "type": "contact",
                "id": "contact-1",
                "value": {
                    "heading": "Kontakt os",
                    "text": "Vi hjælper dig gerne",
                    "address": "Testgade 1, 1234 København",
                    "phone": "+45 12 34 56 78",
                    "email": "test@test.dk",
                },
            }
        ]
        FlexPage.objects.filter(pk=home_page.pk).update(body=json.dumps(body_data))
        home_page.refresh_from_db()
        response = client.get(home_page.url)
        assert response.status_code == 200
        content = response.content.decode()
        assert "Kontakt os" in content
        assert "Testgade 1" in content
        assert "+45 12 34 56 78" in content

    def test_richtext_block_renders(self, client, site, home_page):
        """RichText section block should render."""
        body_data = [
            {
                "type": "richtext",
                "id": "rt-1",
                "value": {
                    "heading": "Vores historie",
                    "content": "<p>Lang og spændende historie.</p>",
                    "background": "light",
                },
            }
        ]
        FlexPage.objects.filter(pk=home_page.pk).update(body=json.dumps(body_data))
        home_page.refresh_from_db()
        response = client.get(home_page.url)
        assert response.status_code == 200
        content = response.content.decode()
        assert "Vores historie" in content

    def test_spacer_block_renders(self, client, site, home_page):
        """Spacer block should render a div with height."""
        body_data = [
            {
                "type": "spacer",
                "id": "spacer-1",
                "value": {"height": "medium"},
            }
        ]
        FlexPage.objects.filter(pk=home_page.pk).update(body=json.dumps(body_data))
        home_page.refresh_from_db()
        response = client.get(home_page.url)
        assert response.status_code == 200
        content = response.content.decode()
        assert "4rem" in content

    def test_projects_showcase_block_renders_without_projects_page(
        self, client, site, home_page
    ):
        """ProjectsShowcase block with no projects_page should render gracefully."""
        body_data = [
            {
                "type": "projects_showcase",
                "id": "ps-1",
                "value": {
                    "heading": "Aktuelle projekter",
                    "projects_page": None,
                    "count": 3,
                    "button_text": "Alle projekter",
                },
            }
        ]
        FlexPage.objects.filter(pk=home_page.pk).update(body=json.dumps(body_data))
        home_page.refresh_from_db()
        response = client.get(home_page.url)
        assert response.status_code == 200
        content = response.content.decode()
        assert "Aktuelle projekter" in content

    def test_projects_showcase_block_renders_with_projects(
        self, client, site, home_page, project_index, project_page
    ):
        """ProjectsShowcase block should show actual project cards."""
        body_data = [
            {
                "type": "projects_showcase",
                "id": "ps-1",
                "value": {
                    "heading": "Aktuelle projekter",
                    "projects_page": project_index.pk,
                    "count": 3,
                    "button_text": "Alle projekter",
                },
            }
        ]
        FlexPage.objects.filter(pk=home_page.pk).update(body=json.dumps(body_data))
        home_page.refresh_from_db()
        response = client.get(home_page.url)
        assert response.status_code == 200
        content = response.content.decode()
        assert "Test Projekt" in content

    def test_subpage_types(self):
        assert "home.FlexPage" in FlexPage.subpage_types
        assert "projects.ProjectIndexPage" in FlexPage.subpage_types

    def test_parent_page_types(self):
        assert "wagtailcore.Page" in FlexPage.parent_page_types
        assert "home.FlexPage" in FlexPage.parent_page_types

    def test_body_field_exists(self):
        field_names = [f.name for f in FlexPage._meta.get_fields()]
        assert "body" in field_names

    def test_content_panels_include_body(self):
        from wagtail.admin.panels import FieldPanel

        panel_fields = [
            p.field_name for p in FlexPage.content_panels if isinstance(p, FieldPanel)
        ]
        assert "body" in panel_fields

    def test_site_settings_in_context(self, client, site, home_page):
        response = client.get(home_page.url)
        assert "site_settings" in response.context
        assert response.context["site_settings"] is not None

    def test_root_page_in_context(self, client, site, home_page):
        response = client.get(home_page.url)
        assert "root_page" in response.context

    def test_navigation_pages_in_context(self, client, site, home_page, project_index):
        """navigation_pages context variable should include pages with show_in_menus=True."""
        response = client.get(home_page.url)
        assert "navigation_pages" in response.context
        nav_pages = list(response.context["navigation_pages"])
        # ProjectIndexPage was created with show_in_menus=True
        titles = [p.title for p in nav_pages]
        assert "Projekter" in titles

    def test_navigation_pages_from_context_processor(self, client, site, home_page, project_index):
        """Pages NOT in menu should not appear in navigation_pages."""
        # Create a page with show_in_menus=False (default)
        hidden_page = FlexPage(title="Hidden", slug="hidden", show_in_menus=False)
        home_page.add_child(instance=hidden_page)
        response = client.get(home_page.url)
        nav_pages = list(response.context["navigation_pages"])
        titles = [p.title for p in nav_pages]
        assert "Hidden" not in titles


@pytest.mark.django_db
class TestSiteSettings:
    def test_site_settings_model_fields_exist(self):
        field_names = [f.name for f in SiteSettings._meta.get_fields()]
        for field in [
            "site_name",
            "tagline",
            "opening_hours",
            "footer_text",
            "address",
            "phone",
            "email",
        ]:
            assert field in field_names, f"Field '{field}' missing from SiteSettings"

    def test_site_settings_defaults(self, site):
        settings = SiteSettings.for_site(site)
        assert settings is not None
        assert settings.site_name == "Test Site"

    def test_site_settings_contact_fields(self, site):
        settings = SiteSettings.for_site(site)
        assert settings.address == "Testgade 1"
        assert settings.phone == "+45 12 34 56 78"
        assert settings.email == "test@example.com"

    def test_site_settings_for_site(self, site):
        settings = SiteSettings.for_site(site)
        assert settings.site is not None

    def test_footer_renders_settings_address(self, client, site, home_page):
        """Footer should display address from SiteSettings."""
        response = client.get(home_page.url)
        content = response.content.decode()
        assert "Testgade 1" in content

    def test_footer_renders_settings_phone(self, client, site, home_page):
        """Footer should display phone from SiteSettings."""
        response = client.get(home_page.url)
        content = response.content.decode()
        assert "+45 12 34 56 78" in content

    def test_footer_renders_settings_email(self, client, site, home_page):
        """Footer should display email from SiteSettings."""
        response = client.get(home_page.url)
        content = response.content.decode()
        assert "test@example.com" in content


class TestFlexPageStructure(WagtailPageTestCase):
    def test_can_create_project_index_under_flex_page(self):
        from apps.projects.models import ProjectIndexPage

        self.assertCanCreateAt(FlexPage, ProjectIndexPage)

    def test_can_create_flex_page_under_flex_page(self):
        self.assertCanCreateAt(FlexPage, FlexPage)
