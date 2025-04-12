from django.core.management.base import BaseCommand
from resources.models import ResourceType

class Command(BaseCommand):
    help = 'Creates default resource types'

    def handle(self, *args, **options):
        default_types = [
            'Notes',
            'Question Papers',
            'Assignments',
            'Presentations',
            'Video Lectures',
            'Lab Manuals',
            'Reference Books',
            'Study Materials',
            'Syllabus',
            'Course Plan'
        ]

        created_count = 0
        existing_count = 0

        for type_name in default_types:
            resource_type, created = ResourceType.objects.get_or_create(name=type_name)
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'Created resource type: {type_name}'))
            else:
                existing_count += 1
                self.stdout.write(self.style.WARNING(f'Resource type already exists: {type_name}'))

        self.stdout.write(self.style.SUCCESS(
            f'\nSummary:\nCreated: {created_count}\nAlready Existing: {existing_count}\nTotal: {len(default_types)}'
        ))
