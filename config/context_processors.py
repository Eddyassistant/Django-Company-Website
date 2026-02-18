from wagtail.models import Site


def site_settings(request):
    """Inject SiteSettings, root page, and navigation pages into every template context."""
    from apps.home.models import SiteSettings

    try:
        site = Site.find_for_request(request)
        settings = SiteSettings.for_site(site)
        root_page = site.root_page.specific if site and site.root_page else None
        navigation_pages = site.root_page.get_children().live().in_menu() if site and site.root_page else []
    except Exception:
        settings = None
        root_page = None
        navigation_pages = []

    return {
        "site_settings": settings,
        "root_page": root_page,
        "navigation_pages": navigation_pages,
    }
