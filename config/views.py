from django.http import HttpResponse, JsonResponse


def health_check(request):
    return JsonResponse({"status": "healthy"})


def robots_txt(request):
    lines = [
        "User-Agent: *",
        "Allow: /",
        "Sitemap: {}/sitemap.xml".format(request.build_absolute_uri("/").rstrip("/")),
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")
