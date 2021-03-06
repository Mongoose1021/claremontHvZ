import os

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from HVZ.main import models

class Command(BaseCommand):
    def handle(self, *args, **options):

        self.stderr.write("Synchronizing the database...")
        self.delimit()
        call_command('syncdb', interactive=True)

        self.stderr.write("Synchronized!")
        self.delimit()

        try:
            self.stderr.write("Loading colleges data...")
            self.delimit()

            call_command(
                'loaddata',
                os.path.join(
                    settings.PROJECT_PATH,
                    'HVZ', 'main', 'fixtures', 'production.json'
                )
            )

            self.stderr.write("Data loaded!")
            self.delimit()

        except CommandError:
            self.stderr.write("Data loading failed!")

        self.stderr.write("Compiling style files...")
        self.delimit()
        try:
            call_command('compilecss')
        except CommandError:
            self.stderr.write("Style compilation failed!")

        self.stderr.write("Collecting static files...")
        self.delimit()

        try:
            call_command('collectstatic', interactive=False)
        except CommandError:
            self.delimit()
            self.stderr.write("Static file collection failed!")

        if models.Game.objects.count() == 0:
            self.delimit()
            self.stderr.write("Simulating a game...")
            call_command('newgame', stdout=self.stdout, stderr=self.stderr)
            call_command('randomplayers', stdout=self.stdout, stderr=self.stderr)
            call_command('randomhistory', stdout=self.stdout, stderr=self.stderr)
            self.stderr.write("Game created!")

        if models.Game.objects.count() == 0:
            self.delimit()
            self.stderr.write("Simulating a game...")
            call_command('newgame', stdout=self.stdout, stderr=self.stderr)
            self.stderr.write("Game created!")

        if models.Player.current_players().count() == 0:
            self.delimit()
            self.stderr.write("Generating a history...")
            self.delimit()
            call_command('randomplayers', stdout=self.stdout, stderr=self.stderr)
            self.stderr.write("Players created!")
            call_command('randomhistory', stdout=self.stdout, stderr=self.stderr)
            self.stderr.write("Brains eaten!")

        # Unit tests must come last, as running them puts us under a test db
        self.delimit()
        self.stderr.write("Running unit tests...")
        self.delimit()
        call_command('test', 'HVZ', stdout=self.stdout, stderr=self.stderr)

        self.delimit()
        self.stderr.write("Build Complete!")
        self.delimit()
        self.stderr.write(
            "Now run `python manage.py runserver` and go to localhost:8000 in your browser."
        )
        self.delimit()

    def delimit(self):
        self.stderr.write('-' * 79)
