"""Browser tests with Playwright.

These tests require:
- pytest-playwright (included in dependency-groups.dev)
- Chromium: run `uv run playwright install chromium` once
- browser_demo_data session fixture (see conftest.py) which commits demo data
  to the database so the live_server thread can see it.
"""
import pytest
from playwright.sync_api import Page, expect


@pytest.mark.django_db
def test_homepage_loads(page: Page, live_server, browser_demo_data):
    """Test homepage loads with correct title."""
    page.goto(live_server.url)
    expect(page).to_have_title("Snedkeri Meier | Snedkeri Meier")
    expect(page.locator("h1")).to_contain_text("Snedkeri Meier")


@pytest.mark.django_db
def test_homepage_has_navigation(page: Page, live_server, browser_demo_data):
    """Test navbar has correct links."""
    page.goto(live_server.url)
    expect(page.locator("nav")).to_be_visible()
    expect(page.locator("nav a:has-text('Projekter')")).to_be_visible()


@pytest.mark.django_db
def test_projects_page_loads(page: Page, live_server, browser_demo_data):
    """Test projects page loads."""
    page.goto(f"{live_server.url}/projekter/")
    expect(page).to_have_title("Projekter | Snedkeri Meier")
    expect(page.locator("h1")).to_contain_text("Projekter")


@pytest.mark.django_db
def test_projects_page_shows_cards(page: Page, live_server, browser_demo_data):
    """Test project cards are visible."""
    page.goto(f"{live_server.url}/projekter/")
    cards = page.locator(".card")
    expect(cards).to_have_count(3)


@pytest.mark.django_db
def test_project_detail_loads(page: Page, live_server, browser_demo_data):
    """Test individual project page loads."""
    page.goto(f"{live_server.url}/projekter/restaurering-barokskab/")
    expect(page.locator("h1")).to_contain_text("Restaurering af barokskab")


@pytest.mark.django_db
def test_admin_redirects_to_login(page: Page, live_server, browser_demo_data):
    """Test admin page redirects when not logged in."""
    page.goto(f"{live_server.url}/admin/")
    expect(page).to_have_url(f"{live_server.url}/admin/login/?next=/admin/")


@pytest.mark.django_db
def test_homepage_shows_hero_section(page: Page, live_server, browser_demo_data):
    """Test homepage renders the hero block."""
    page.goto(live_server.url)
    # Hero title rendered in h1
    expect(page.locator(".hero-section h1")).to_contain_text("Snedkeri Meier")


@pytest.mark.django_db
def test_homepage_shows_projects_showcase(page: Page, live_server, browser_demo_data):
    """Test homepage renders the projects showcase block with project cards."""
    page.goto(live_server.url)
    # The projects showcase section should show project cards
    cards = page.locator(".card")
    expect(cards.first).to_be_visible()


@pytest.mark.django_db
def test_footer_shows_contact_info(page: Page, live_server, browser_demo_data):
    """Test footer shows contact information from SiteSettings."""
    page.goto(live_server.url)
    footer = page.locator("footer")
    expect(footer).to_contain_text("Snedkeri Meier")
    expect(footer).to_contain_text("Bredgade")
