from django.core.management.base import BaseCommand
from resources.models import AcademicYear, Semester

class Command(BaseCommand):
    help = 'Creates default academic years and semesters'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating default academic years...')
        AcademicYear.create_defaults()
        self.stdout.write(self.style.SUCCESS('Successfully created academic years'))

        self.stdout.write('Creating default semesters...')
        Semester.create_defaults()
        self.stdout.write(self.style.SUCCESS('Successfully created semesters'))
