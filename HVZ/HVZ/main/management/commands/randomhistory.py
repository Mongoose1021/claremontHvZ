from datetime import datetime, time, timedelta
import random
from optparse import make_option

from django.core.management import call_command
from django.core.management.base import BaseCommand

from HVZ.main.models import Player, Game, Building
from HVZ.feed.models import Meal


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option(
            '-m',
            '--meals',
            type='int',
        ),
        make_option(
            '-p',
            '--players',
            type='int',
        ),
        make_option(
            '-z',
            '--ozs',
            type='int',
        ),
        make_option(
            '--password',
            type='string',
        ),
    )

    def handle(self, *args, **options):
        try:
            self.game = Game.imminent_game()
        except Game.DoesNotExist:
            # Create game and players
            call_command(
                'randomplayers',
                players=options.get('players'),
                ozs=options.get('ozs'),
                password=options.get('password'),
                stdout=self.stdout,
                stderr=self.stderr,
            )
            self.game = Game.imminent_game()

        humans = Player.current_players().filter(team='H')
        zombies = Player.current_players().filter(team='Z')
        if not len(humans) or not len(zombies):
            self.stderr.write(
                '\n'.join(["There are no players in the current game.",
                           "To generate a batch of random players, run",
                           "    ./manage.py randomplayers"]))
            return

        num_meals = options.get('meals') or len(humans) / 2

        self.stdout.write("Creating {} meals".format(num_meals))

        if not num_meals:
            return

        if len(humans) < num_meals:
            self.stderr.write(
                "There are only {} humans in the current game.".format(len(humans))
            )
            num_meals = len(humans)

        meals = self.make_meals(num_meals)
        Meal.objects.bulk_create(meals)

    def make_meals(self, num_meals):
        humans = list(Player.current_players().filter(team='H'))
        zombies = list(Player.current_players().filter(team='Z'))
        
        g = Game.imminent_game()

        days = (g.end_date - g.start_date).days

        day = g.start_date
        while day < g.end_date:

            meals_per_hour = [0 for i in xrange(24)]
            for i in xrange(int(num_meals / days)):
                meals_per_hour[int(random.gauss(13, 4)) % 24] += 1

            for hour in xrange(24):

                for meal in xrange(meals_per_hour[hour]):
                    z = int(random.random() * len(zombies))
                    h = int(random.random() * len(humans))

                    Meal(
                        eater=zombies[z],
                        eaten=humans[h],
                        time=datetime.combine(day, time(hour=hour)),
                        location=random.choice(Building.objects.all()),
                    ).save()

                    # Instead of retrieving the entire zombie and human lists
                    # again, why don't we just add the human to the zombie
                    # horde ourselves?
                    zombies.append(humans.pop(h))

            day += timedelta(days=1)
