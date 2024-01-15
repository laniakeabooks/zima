from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from main import models


class Command(BaseCommand):
    help = "Match people with same interests."

    def log(self, message=""):
        self.stdout.write(self.style.NOTICE(message))

    def handle(self, *args, **options):
        self.log("Starting scan...")
        models.Matchlog.objects.create()

        # base algorithm:
        # cycle through all entries
        # for each entry
        #     find all entries with same resource except itself
        #     for each entry with same resource
        #         check if it is inside .has_received of top-level entry
        #         if not, send email, and add
        # done

        two_days_ago = timezone.now() - timedelta(days=2)
        for entry in models.Entry.objects.all():
            # ignore if entry is too new
            if entry.created_at > two_days_ago:
                self.log(f"ignoring {entry}, was created in the last two days")
                continue

            self.log(f"now checking {entry}")
            same_resource_entry_list = models.Entry.objects.filter(
                resource=entry.resource
            ).exclude(id=entry.id)
            self.log(
                f"    found {len(same_resource_entry_list)} entries with same resource"
            )
            for sr_entry in same_resource_entry_list:
                if sr_entry in entry.has_received.all():
                    self.log(f"    {entry} has received {sr_entry}")
                else:
                    self.log(f"    {entry} has never received {sr_entry}")

                    # give 2 days buffer
                    if sr_entry.created_at > two_days_ago:
                        self.log(
                            f"    ignoring {sr_entry}, was created in the last two days"
                        )
                        continue

                    self.log(f"        sending: {timezone.now()}")
                    entry.has_received.add(sr_entry)
            self.log()
