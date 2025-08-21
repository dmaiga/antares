# jobs/templatetags/utils.py

from django import template
from django.utils.safestring import mark_safe
from bs4 import BeautifulSoup

register = template.Library()

@register.filter
def clean_truncate_html(job, args):
    """
    Usage: {{ job|clean_truncate_html:"taches,5,3" }}
    args: champ, max_mots_total, max_li
    Exemple: "taches,5,3" -> max 5 mots, max 3 <li>
    """
    try:
        field_name, max_words, max_li = args.split(',')
        max_words = int(max_words)
        max_li = int(max_li)
    except ValueError:
        return ''

    html_content = getattr(job, f"get_clean_html")(field_name)
    if not html_content:
        return ''

    html_content = html_content.replace('&nbsp;', ' ')
    soup = BeautifulSoup(html_content, 'html.parser')

    # Limiter le nombre de <li>
    li_tags = soup.find_all('li')
    if li_tags:
        for i, li in enumerate(li_tags):
            if i >= max_li:
                li.decompose()  # supprime les <li> après la limite
            else:
                # Tronquer les mots de chaque <li> si nécessaire
                words = li.get_text(strip=True).split()
                if len(words) > max_words:
                    li.string = ' '.join(words[:max_words]) + '...'

    else:
        # Pas de <li> -> tronquer le texte global
        text = soup.get_text(separator=' ', strip=True).split()
        if len(text) > max_words:
            truncated_text = ' '.join(text[:max_words]) + '...'
            return mark_safe(truncated_text)

    return mark_safe(str(soup))

