import pytest
from wagtail.models import Page, Site


@pytest.fixture
def root_page(db):
    root = Page.objects.get(depth=1)
    # Delete any default Wagtail welcome pages to avoid slug conflicts
    root.get_children().delete()
    # Fix treebeard tree after bulk delete to avoid MP tree inconsistencies
    Page.fix_tree()
    root.refresh_from_db()
    return root


@pytest.fixture
def home_page(db, root_page):
    from apps.home.models import FlexPage

    home = FlexPage(
        title="Test Home",
        slug="home",
    )
    root_page.add_child(instance=home)
    return home


@pytest.fixture
def site(db, home_page):
    from apps.home.models import SiteSettings

    Site.objects.all().delete()
    s = Site.objects.create(
        hostname="localhost",
        port=80,
        root_page=home_page,
        is_default_site=True,
    )
    # Create SiteSettings for the site so the context processor has data
    SiteSettings.objects.update_or_create(
        site=s,
        defaults={
            "site_name": "Test Site",
            "tagline": "Test tagline",
            "opening_hours": "Man - Fre: 9:00 - 17:00",
            "address": "Testgade 1",
            "phone": "+45 12 34 56 78",
            "email": "test@example.com",
        },
    )
    return s


@pytest.fixture
def project_index(db, home_page):
    from apps.projects.models import ProjectIndexPage

    index = ProjectIndexPage(
        title="Projekter",
        slug="projekter",
        intro="Vores projekter",
        show_in_menus=True,
    )
    home_page.add_child(instance=index)
    return index


@pytest.fixture
def project_page(db, project_index):
    import datetime

    from apps.projects.models import ProjectPage

    project = ProjectPage(
        title="Test Projekt",
        slug="test-projekt",
        short_description="Et testprojekt",
        project_date=datetime.date(2024, 1, 15),
        client="Test Kunde",
        location="København",
    )
    project_index.add_child(instance=project)
    return project


# ---------------------------------------------------------------------------
# Browser test fixtures — function-scoped demo data via transactional_db
# ---------------------------------------------------------------------------


@pytest.fixture
def browser_demo_data(transactional_db):
    """Populate demo site data for browser (Playwright) tests.

    Uses transactional_db so committed data is visible to the live_server
    thread across thread boundaries. Re-runs for each test because
    TransactionTestCase flushes the DB on teardown.
    """
    from django.contrib.contenttypes.models import ContentType
    from django.core.management import call_command
    from wagtail.models import Locale, Page

    # After TransactionTestCase flush, ALL data is gone including the Wagtail
    # root page created by migrations. We need to recreate it before setup_demo_site.
    if not Page.objects.filter(depth=1).exists():
        locale, _ = Locale.objects.get_or_create(language_code="en")
        root_content_type = ContentType.objects.get_for_model(Page)
        Page.add_root(
            title="Root",
            slug="root",
            content_type=root_content_type,
            locale=locale,
        )

    call_command("setup_demo_site")
