from django import template

register = template.Library()

@register.filter
def split(value, delimiter=','):
    return value.split(delimiter) if value else []

@register.filter
def trim(value):
    return value.strip() if value else ''

@register.filter
def get_status_color(statut):
    colors = {
        'POSTULE': 'info',
        'EN_REVUE': 'primary',
        'ENTRETIEN': 'warning',
        'ACCEPTE': 'success',
        'REFUSE': 'danger',
        'RETIRE': 'secondary',
    }
    return colors.get(statut, 'secondary')

@register.filter
def get_status_icon(statut):
    icons = {
        'POSTULE': 'paper-plane',
        'EN_REVUE': 'eye',
        'ENTRETIEN': 'calendar-alt',
        'ACCEPTE': 'check-circle',
        'REFUSE': 'times-circle',
        'RETIRE': 'ban',
    }
    return icons.get(statut, 'question-circle')