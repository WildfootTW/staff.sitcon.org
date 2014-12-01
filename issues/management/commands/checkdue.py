from django.conf import settings
from django.core.management.base import NoArgsCommand
from django.utils import timezone
from issues.models import Issue
from notifications.utils import format_address, send_template_email

class Command(NoArgsCommand):
	help = "Checks and sends SMS from notification queue."

	def handle_noargs(self, **options):
		time_delta = settings.ISSUE_EXPIRE_TIMEDELTA
		time_range = (timezone.now() - time_delta, timezone.now() + time_delta)
		
		issues = Issue.objects.filter(is_open=True, due_time__range=time_range)
		for issue in issues:
			for watcher in issue.starring.all():
				send_template_email(
					settings.DEFAULT_ISSUE_SENDER,
					format_address(watcher.profile.name(), watcher.email),
					'mail/issue_expired.html',
					{
						'issue': issue,
						'receiver': watcher,
					}
				)