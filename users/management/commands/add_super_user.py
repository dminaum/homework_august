from django.core.management import BaseCommand
from users.models import CustomUser


class Command(BaseCommand):

    def handle(self, *args, **options):
        user = CustomUser.objects.create(email='test1@mail.ru', is_staff=True, is_superuser=True)
        user.set_password('12345')
        user.save()
        self.stdout.write(self.style.SUCCESS('Суперпользователь создан'))
