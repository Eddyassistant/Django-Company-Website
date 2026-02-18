import pytest


@pytest.mark.django_db
class TestSearchView:
    def test_search_page_loads(self, client, site):
        response = client.get("/search/")
        assert response.status_code == 200

    def test_search_with_empty_query(self, client, site):
        response = client.get("/search/?query=")
        assert response.status_code == 200
        assert len(response.context["search_results"]) == 0

    def test_search_without_query_param(self, client, site):
        response = client.get("/search/")
        assert response.context["search_query"] is None
        assert len(response.context["search_results"]) == 0

    def test_search_with_query(self, client, site, home_page):
        response = client.get("/search/?query=Test")
        assert response.status_code == 200
        assert "search_results" in response.context
        assert "search_query" in response.context
        assert response.context["search_query"] == "Test"

    def test_search_with_valid_query_returns_200(self, client, site, home_page, project_index, project_page):
        """Search with a real query should return 200 (results depend on search backend)."""
        response = client.get("/search/?query=Projekt")
        assert response.status_code == 200
        assert "search_results" in response.context

    def test_search_returns_200_for_no_match(self, client, site, home_page):
        response = client.get("/search/?query=xyzzy12345nonexistent")
        assert response.status_code == 200

    def test_search_uses_correct_template(self, client, site):
        response = client.get("/search/")
        assert "search/search.html" in [t.name for t in response.templates]

    def test_search_pagination_invalid_page(self, client, site, home_page):
        """Invalid page number should fall back to page 1."""
        response = client.get("/search/?query=Test&page=abc")
        assert response.status_code == 200

    def test_search_pagination_empty_page(self, client, site, home_page):
        """Out-of-range page number should show last page."""
        response = client.get("/search/?query=Test&page=999")
        assert response.status_code == 200
