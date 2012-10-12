from django import template
from django.db.models import Q
from django.utils import timezone

from announcements.models import Announcement


register = template.Library()


class AnnouncementsNode(template.Node):
    @classmethod
    def handle_token(cls, parser, token):
        bits = token.split_contents()
        if len(bits) != 3:
            raise template.TemplateSyntaxError
        return cls(as_var=bits[2])

    def __init__(self, as_var):
        self.as_var = as_var

    def render(self, context):
        request = context["request"]
        qs = Announcement.current()

        exclusions = request.session.get("excluded_announcements", [])
        exclusions = set(exclusions)
        if request.user.is_authenticated():
            for dismissal in request.user.announcement_dismissals.all():
                exclusions.add(dismissal.announcement_id)
        else:
            qs = [announcement for announcement in qs if not announcement.members_only]
        context[self.as_var] = [announcement for announcement in qs if announcement.pk not in exclusions]
        return ""


@register.tag
def announcements(parser, token):
    """
    Usage::
        {% announcements as var %}

    Returns a list of announcements
    """
    return AnnouncementsNode.handle_token(parser, token)
