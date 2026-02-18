import datetime

import pytest

from apps.projects.models import ProjectIndexPage, ProjectPage


@pytest.mark.django_db
class TestProjectIndexPage:
    def test_renders(self, client, site, project_index):
        response = client.get(project_index.url)
        assert response.status_code == 200

    def test_correct_template(self, client, site, project_index):
        response = client.get(project_index.url)
        assert "projects/project_index_page.html" in [t.name for t in response.templates]

    def test_project_appears_in_index(self, client, site, project_index, project_page):
        response = client.get(project_index.url)
        assert response.status_code == 200
        content = response.content.decode()
        assert "Test Projekt" in content

    def test_parent_page_types(self):
        assert ProjectIndexPage.parent_page_types == ["home.FlexPage"]

    def test_subpage_types(self):
        assert ProjectIndexPage.subpage_types == ["projects.ProjectPage"]

    def test_projects_in_context(self, client, site, project_index, project_page):
        """Context should include paginated projects."""
        response = client.get(project_index.url)
        assert "projects" in response.context
        assert project_page in response.context["projects"].object_list

    def test_pagination_page_1(self, client, site, home_page, project_index):
        """Pagination: first page with 10 projects (paginator uses 9 per page)."""
        for i in range(10):
            p = ProjectPage(
                title=f"Projekt {i}",
                slug=f"projekt-{i}",
                short_description=f"Beschreibung {i}",
                project_date=datetime.date(2024, 1, i + 1),
                client=f"Kunde {i}",
                location="München",
            )
            project_index.add_child(instance=p)

        response = client.get(project_index.url + "?page=1")
        assert response.status_code == 200
        assert response.context["projects"].has_other_pages()
        assert response.context["projects"].number == 1

    def test_pagination_page_2(self, client, site, home_page, project_index):
        """Pagination: second page exists when more than 9 projects."""
        for i in range(10):
            p = ProjectPage(
                title=f"Projekt {i}",
                slug=f"projekt-{i}",
                short_description=f"Beschreibung {i}",
                project_date=datetime.date(2024, 1, i + 1),
                client=f"Kunde {i}",
                location="München",
            )
            project_index.add_child(instance=p)

        response = client.get(project_index.url + "?page=2")
        assert response.status_code == 200
        assert response.context["projects"].number == 2

    def test_streamfield_content_renders(self, client, site, project_index):
        """StreamField body content should render in the template."""
        import json

        project = ProjectPage(
            title="Projekt mit Inhalt",
            slug="projekt-mit-inhalt",
            short_description="Test",
            project_date=datetime.date(2024, 1, 1),
            client="Kunde",
            location="München",
        )
        project_index.add_child(instance=project)
        # Set StreamField body via direct DB update
        body_data = [
            {"type": "heading", "value": "Projekttitel", "id": "test-heading-1"},
            {"type": "paragraph", "value": "<p>Projektbeschreibung</p>", "id": "test-para-1"},
        ]
        ProjectPage.objects.filter(pk=project.pk).update(body=json.dumps(body_data))
        project.refresh_from_db()

        response = client.get(project.url)
        assert response.status_code == 200
        content = response.content.decode()
        assert "Projekttitel" in content


@pytest.mark.django_db
class TestProjectPage:
    def test_renders(self, client, site, project_page):
        response = client.get(project_page.url)
        assert response.status_code == 200

    def test_correct_template(self, client, site, project_page):
        response = client.get(project_page.url)
        assert "projects/project_page.html" in [t.name for t in response.templates]

    def test_parent_page_types(self):
        assert ProjectPage.parent_page_types == ["projects.ProjectIndexPage"]

    def test_subpage_types(self):
        assert ProjectPage.subpage_types == []

    def test_model_fields_exist(self):
        """All required fields should exist on ProjectPage."""
        field_names = [f.name for f in ProjectPage._meta.get_fields()]
        for field in ["short_description", "project_date", "client", "location", "main_image", "body"]:
            assert field in field_names, f"Field '{field}' missing from ProjectPage"

    def test_content_panels_include_all_fields(self):
        """All content fields should have a panel in content_panels."""
        from wagtail.admin.panels import FieldPanel

        panel_fields = [p.field_name for p in ProjectPage.content_panels if isinstance(p, FieldPanel)]
        for field in ["short_description", "project_date", "client", "location", "main_image", "body"]:
            assert field in panel_fields, f"Field '{field}' missing from ProjectPage.content_panels"

    def test_project_details_in_response(self, client, site, project_page):
        """Project details (client, location, date) should appear on the page."""
        response = client.get(project_page.url)
        content = response.content.decode()
        assert "Test Projekt" in content
        assert "Test Kunde" in content
        assert "København" in content

    def test_project_hierarchy(self, project_index, project_page):
        """ProjectPage should be a child of ProjectIndexPage."""
        assert project_page.get_parent().specific == project_index
