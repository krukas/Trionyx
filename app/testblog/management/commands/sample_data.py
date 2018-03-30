import random

from django.core.management.base import BaseCommand
from django.utils import timezone

from app.testblog.models import Category, Post


class Command(BaseCommand):
    help = 'Install/Update sample data'

    def handle(self, *args, **options):
        categories = [
            'Python3', 'Python2', 'PHP', 'Haskell', 'SQL', 'Java', 'Javascript', 'C#', 'C++', 'Ruby',
            'Basic', 'Lisp', 'Lua', 'Perl', 'Erlang', 'F#', 'C', 'Cobol', 'go', 'Rust', 'Fortran', 'Objective-C',
            'Smalltalk', 'Turing', 'Bash', 'VBScript', 'HTML', 'CSS', 'XML', 'JSON', 'Scala', 'IO'
        ]

        categories_objects = []
        for category in categories:
            cat = Category(name=category, description=category)
            cat.save()
            categories_objects.append(cat)

        for x in range(100):
            cat = random.choice(categories_objects)
            Post(
                title='Blog post {} about {}'.format(x, str(cat)),
                content='some content',
                publish_date=timezone.now(),
                category=cat,
            ).save()


