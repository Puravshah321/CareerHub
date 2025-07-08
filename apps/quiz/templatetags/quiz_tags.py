from django import template
from ..models import GlobalRanking

register = template.Library()

@register.simple_tag(takes_context=True)
def get_user_score(context):
    user = context['request'].user
    if user.is_authenticated:
        try:
            return GlobalRanking.objects.get(user=user).total_score
        except GlobalRanking.DoesNotExist:
            return 0
    return ""
