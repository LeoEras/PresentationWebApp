from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag
def render_stars(rating, max_stars=5):
    html = ""
    full_stars = int(rating)
    half_star = (rating - full_stars) >= 0.5
    empty_stars = max_stars - full_stars - (1 if half_star else 0)

    for _ in range(full_stars):
        html += '<i class="fa-solid fa-star text-warning"></i> '

    if half_star:
        html += '<i class="fa-solid fa-star-half-stroke text-warning"></i> '

    for _ in range(empty_stars):
        html += '<i class="fa-regular fa-star text-warning"></i> '

    return mark_safe(html)