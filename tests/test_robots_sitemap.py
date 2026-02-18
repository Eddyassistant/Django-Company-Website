"""Tests for robots.txt and sitemap.xml endpoints."""

import pytest


@pytest.mark.django_db
class TestRobotsTxt:
    def test_robots_txt_returns_200(self, client, site):
        response = client.get("/robots.txt")
        assert response.status_code == 200

    def test_robots_txt_content_type(self, client, site):
        response = client.get("/robots.txt")
        assert response["Content-Type"] == "text/plain"

    def test_robots_txt_contains_sitemap(self, client, site):
        response = client.get("/robots.txt")
        content = response.content.decode()
        assert "sitemap.xml" in content

    def test_robots_txt_allows_all(self, client, site):
        response = client.get("/robots.txt")
        content = response.content.decode()
        assert "User-Agent: *" in content
        assert "Allow: /" in content


@pytest.mark.django_db
class TestSitemapXml:
    def test_sitemap_returns_200(self, client, site, home_page):
        response = client.get("/sitemap.xml")
        assert response.status_code == 200

    def test_sitemap_is_xml(self, client, site, home_page):
        response = client.get("/sitemap.xml")
        assert "xml" in response["Content-Type"]
