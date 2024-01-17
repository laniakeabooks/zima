from datetime import timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.utils import timezone

from main import models


class Command(BaseCommand):
    help = "Match people with same interests."

    def log(self, message=""):
        self.stdout.write(self.style.NOTICE(message))

    def inform_entries(self, *, receiver_entry, content_entry_list):
        """
        Send email to receiver_entry about content_entry_list.
        """
        subject = f"01z.co Matches on {receiver_entry.resource}"
        content = render_to_string(
            "main/match_email.txt",
            {
                "entry_list": content_entry_list,
            },
        )
        send_mail(subject, content, settings.DEFAULT_FROM_EMAIL, [receiver_entry.email])

    def handle(self, *args, **options):
        self.log("Starting scan...")

        # base algorithm:
        # cycle through all entries
        # for each entry
        #     find all entries with same resource except itself
        #     for each entry with same resource
        #         check if it is inside .has_received of top-level entry
        #         if not, send email, and add .has_received
        # done

        two_days_ago = timezone.now() - timedelta(days=2)
        entry_list = models.Entry.objects.filter(is_approved=True)
        self.log(f"found {entry_list.count()} approved entries")
        for entry in entry_list:

            # ignore if entry is too new
            if entry.created_at > two_days_ago:
                self.log(f"ignoring {entry}, was created in the last two days")
                continue

            self.log(f"now checking {entry}")
            models.Matchlog.objects.create(receiver=entry)
            same_resource_entry_list = models.Entry.objects.filter(
                is_approved=True,
                resource=entry.resource,
            ).exclude(id=entry.id)  # exclude self entry
            self.log(
                f"    found {len(same_resource_entry_list)} entries with same resource"
            )

            content_entry_list = []
            # for each matching entry with same resource
            for sr_entry in same_resource_entry_list:
                if sr_entry in entry.has_received.all():
                    # case when entry has already been sent
                    self.log(f"    {entry} has received {sr_entry}")
                else:
                    # case when entry has not been sent
                    self.log(f"    {entry} has never received {sr_entry}")

                    # 2 days buffer
                    if sr_entry.created_at > two_days_ago:
                        self.log(f"    ignoring {sr_entry}, created in the last 2 days")
                        continue

                    # keep track that we have now matched these entries
                    content_entry_list.append(sr_entry)
                    entry.has_received.add(sr_entry)

            self.log(f"        sending: {timezone.now()}")
            self.inform_entries(
                receiver_entry=entry,
                content_entry_list=content_entry_list,
            )

            # log empty line for readability
            self.log()
        self.log("End scan")
