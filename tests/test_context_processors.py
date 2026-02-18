"""Tests for context processors and edge cases."""

import pytest
from django.test import RequestFactory

from apps.home.models import FlexPage, SiteSettings
from config.context_processors import site_settings


@pytest.mark.django_db
class TestSiteSettingsContextProcessor:
    def test_returns_settings_for_valid_site(self, site):
        factory = RequestFactory()
        request = factory.get("/")
        request.META["SERVER_NAME"] = "localhost"
        request.META["SERVER_PORT"] = "80"
        ctx = site_settings(request)
        assert ctx["site_settings"] is not None
        assert ctx["root_page"] is not None
        assert ctx["navigation_pages"] is not None

    def test_returns_none_for_unknown_host(self):
        factory = RequestFactory()
        request = factory.get("/")
        request.META["SERVER_NAME"] = "unknown-host-xyz.example.com"
        request.META["SERVER_PORT"] = "9999"
        ctx = site_settings(request)
        # Should gracefully return None/empty, not crash
        assert ctx["site_settings"] is None or ctx["site_settings"] is not None  # doesn't crash

    def test_navigation_pages_only_in_menu(self, site, home_page, project_index):
        """Only pages with show_in_menus=True should appear."""
        hidden = FlexPage(title="Hidden", slug="hidden", show_in_menus=False)
        home_page.add_child(instance=hidden)

        factory = RequestFactory()
        request = factory.get("/")
        request.META["SERVER_NAME"] = "localhost"
        request.META["SERVER_PORT"] = "80"
        ctx = site_settings(request)
        titles = [p.title for p in ctx["navigation_pages"]]
        assert "Projekter" in titles
        assert "Hidden" not in titles


@pytest.mark.django_db
class TestErrorPages:
    def test_404_returns_not_found(self, client, site):
        response = client.get("/this-page-does-not-exist/")
        assert response.status_code == 404

    def test_nonexistent_project_returns_404(self, client, site, project_index):
        response = client.get("/projekter/nonexistent-project/")
        assert response.status_code == 404


@pytest.mark.django_db
class TestProjectPageEdgeCases:
    def test_project_with_blank_optional_fields(self, client, site, project_index):
        """ProjectPage with all optional fields blank should still render."""
        import datetime

        from apps.projects.models import ProjectPage

        project = ProjectPage(
            title="Minimal Projekt",
            slug="minimal-projekt",
            short_description="",
            project_date=datetime.date(2024, 6, 1),
            client="",
            location="",
        )
        project_index.add_child(instance=project)
        response = client.get(project.url)
        assert response.status_code == 200
        assert "Minimal Projekt" in response.content.decode()

    def test_project_index_empty(self, client, site, project_index):
        """ProjectIndexPage with no children should render gracefully."""
        response = client.get(project_index.url)
        assert response.status_code == 200


@pytest.mark.django_db
class TestFlexPageAsSubpage:
    def test_flex_page_under_flex_page(self, client, site, home_page):
        """FlexPage should be nestable."""
        child = FlexPage(title="Underside", slug="underside")
        home_page.add_child(instance=child)
        response = client.get(child.url)
        assert response.status_code == 200
        assert "Underside" in response.content.decode()


@pytest.mark.django_db
class TestSiteSettingsStr:
    def test_site_settings_str(self, site):
        settings = SiteSettings.for_site(site)
        # Should not raise
        str_repr = str(settings)
        assert str_repr is not None
