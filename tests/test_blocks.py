"""Tests for all StreamField blocks — rendering, edge cases, composability."""

import json

import pytest

from apps.home.models import FlexPage


@pytest.mark.django_db
class TestCTABlock:
    def test_cta_block_renders(self, client, site, home_page):
        body_data = [
            {
                "type": "cta",
                "id": "cta-1",
                "value": {
                    "heading": "Klar til at starte?",
                    "text": "Kontakt os i dag",
                    "button_text": "Ring nu",
                    "button_link": None,
                    "button_url": "",
                    "background": "primary",
                },
            }
        ]
        FlexPage.objects.filter(pk=home_page.pk).update(body=json.dumps(body_data))
        response = client.get(home_page.url)
        assert response.status_code == 200
        content = response.content.decode()
        assert "Klar til at starte?" in content
        assert "Kontakt os i dag" in content
        # Button not rendered without link or URL (correct template behavior)
        assert "Ring nu" not in content

    def test_cta_block_with_external_url(self, client, site, home_page):
        body_data = [
            {
                "type": "cta",
                "id": "cta-2",
                "value": {
                    "heading": "Besøg os",
                    "text": "",
                    "button_text": "Google Maps",
                    "button_link": None,
                    "button_url": "https://maps.google.com",
                    "background": "dark",
                },
            }
        ]
        FlexPage.objects.filter(pk=home_page.pk).update(body=json.dumps(body_data))
        response = client.get(home_page.url)
        assert response.status_code == 200
        content = response.content.decode()
        assert "https://maps.google.com" in content


@pytest.mark.django_db
class TestLocationBlock:
    def test_location_block_renders(self, client, site, home_page):
        body_data = [
            {
                "type": "location",
                "id": "loc-1",
                "value": {
                    "heading": "Find os",
                    "address": "Bredgade 42, 1260 København",
                    "map_embed": "",
                },
            }
        ]
        FlexPage.objects.filter(pk=home_page.pk).update(body=json.dumps(body_data))
        response = client.get(home_page.url)
        assert response.status_code == 200
        content = response.content.decode()
        assert "Find os" in content
        assert "Bredgade 42" in content

    def test_location_block_with_map_embed(self, client, site, home_page):
        embed_html = '<iframe src="https://maps.google.com/embed"></iframe>'
        body_data = [
            {
                "type": "location",
                "id": "loc-2",
                "value": {
                    "heading": "Kort",
                    "address": "Testgade 1",
                    "map_embed": embed_html,
                },
            }
        ]
        FlexPage.objects.filter(pk=home_page.pk).update(body=json.dumps(body_data))
        response = client.get(home_page.url)
        assert response.status_code == 200
        assert "maps.google.com" in response.content.decode()


@pytest.mark.django_db
class TestTestimonialsBlock:
    def test_testimonials_block_renders(self, client, site, home_page):
        body_data = [
            {
                "type": "testimonials",
                "id": "test-1",
                "value": {
                    "heading": "Kundeanmeldelser",
                    "testimonials": [
                        {
                            "quote": "Fantastisk arbejde!",
                            "author": "Hans Jensen",
                            "role": "Privatkunde",
                        },
                        {
                            "quote": "Meget professionelt.",
                            "author": "Marie Nielsen",
                            "role": "",
                        },
                    ],
                },
            }
        ]
        FlexPage.objects.filter(pk=home_page.pk).update(body=json.dumps(body_data))
        response = client.get(home_page.url)
        assert response.status_code == 200
        content = response.content.decode()
        assert "Kundeanmeldelser" in content
        assert "Fantastisk arbejde!" in content
        assert "Hans Jensen" in content
        assert "Marie Nielsen" in content

    def test_testimonials_block_empty_list(self, client, site, home_page):
        body_data = [
            {
                "type": "testimonials",
                "id": "test-2",
                "value": {
                    "heading": "Anmeldelser",
                    "testimonials": [],
                },
            }
        ]
        FlexPage.objects.filter(pk=home_page.pk).update(body=json.dumps(body_data))
        response = client.get(home_page.url)
        assert response.status_code == 200


@pytest.mark.django_db
class TestGalleryBlock:
    def test_gallery_block_renders_without_images(self, client, site, home_page):
        body_data = [
            {
                "type": "gallery",
                "id": "gal-1",
                "value": {
                    "heading": "Galleri",
                    "images": [],
                },
            }
        ]
        FlexPage.objects.filter(pk=home_page.pk).update(body=json.dumps(body_data))
        response = client.get(home_page.url)
        assert response.status_code == 200
        assert "Galleri" in response.content.decode()


@pytest.mark.django_db
class TestAboutBlockVariants:
    def test_about_block_image_position_right(self, client, site, home_page):
        body_data = [
            {
                "type": "about",
                "id": "about-right",
                "value": {
                    "heading": "Om os",
                    "text": "<p>Tekst højre.</p>",
                    "image": None,
                    "image_position": "right",
                },
            }
        ]
        FlexPage.objects.filter(pk=home_page.pk).update(body=json.dumps(body_data))
        response = client.get(home_page.url)
        assert response.status_code == 200
        assert "Om os" in response.content.decode()


@pytest.mark.django_db
class TestMultipleBlocks:
    def test_page_with_multiple_blocks(self, client, site, home_page):
        """A FlexPage with multiple blocks should render all of them."""
        body_data = [
            {
                "type": "hero",
                "id": "hero-1",
                "value": {
                    "title": "Velkommen",
                    "subtitle": "",
                    "image": None,
                    "button_text": "",
                    "button_link": None,
                },
            },
            {
                "type": "richtext",
                "id": "rt-1",
                "value": {
                    "heading": "Vores historie",
                    "content": "<p>Lang historie.</p>",
                    "background": "white",
                },
            },
            {
                "type": "contact",
                "id": "ct-1",
                "value": {
                    "heading": "Skriv til os",
                    "text": "",
                    "address": "",
                    "phone": "",
                    "email": "",
                },
            },
            {
                "type": "spacer",
                "id": "sp-1",
                "value": {"height": "large"},
            },
        ]
        FlexPage.objects.filter(pk=home_page.pk).update(body=json.dumps(body_data))
        response = client.get(home_page.url)
        assert response.status_code == 200
        content = response.content.decode()
        assert "Velkommen" in content
        assert "Vores historie" in content
        assert "Skriv til os" in content
        assert "8rem" in content  # large spacer

    def test_page_with_all_block_types(self, client, site, home_page):
        """Smoke test: a page with every block type should render without errors."""
        hero = {"title": "Hero", "subtitle": "", "image": None, "button_text": "", "button_link": None}
        about = {"heading": "About", "text": "<p>x</p>", "image": None, "image_position": "left"}
        contact = {"heading": "Contact", "text": "", "address": "", "phone": "", "email": ""}
        showcase = {"heading": "Projects", "projects_page": None, "count": 3, "button_text": "Alle"}
        cta = {
            "heading": "CTA",
            "text": "",
            "button_text": "Go",
            "button_link": None,
            "button_url": "",
            "background": "primary",
        }
        body_data = [
            {"type": "hero", "id": "b1", "value": hero},
            {"type": "about", "id": "b2", "value": about},
            {"type": "services", "id": "b3", "value": {"heading": "Services", "services": []}},
            {"type": "projects_showcase", "id": "b4", "value": showcase},
            {"type": "contact", "id": "b5", "value": contact},
            {"type": "location", "id": "b6", "value": {"heading": "Location", "address": "Addr", "map_embed": ""}},
            {"type": "richtext", "id": "b7", "value": {"heading": "Rich", "content": "<p>y</p>"}},
            {"type": "gallery", "id": "b8", "value": {"heading": "Gallery", "images": []}},
            {"type": "cta", "id": "b9", "value": cta},
            {"type": "testimonials", "id": "b10", "value": {"heading": "Reviews", "testimonials": []}},
            {"type": "spacer", "id": "b11", "value": {"height": "small"}},
        ]
        FlexPage.objects.filter(pk=home_page.pk).update(body=json.dumps(body_data))
        response = client.get(home_page.url)
        assert response.status_code == 200
