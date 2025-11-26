"""
Management command to set up admin user and demo data
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.accounts.models import CustomUser


class Command(BaseCommand):
    help = 'Create admin user for Django admin panel'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            default='admin@admin.com',
            help='Admin email address'
        )
        parser.add_argument(
            '--password',
            type=str,
            default='admin123',
            help='Admin password'
        )

    def handle(self, *args, **options):
        email = options['email']
        password = options['password']

        with transaction.atomic():
            # Create admin user if doesn't exist
            admin_user, created = CustomUser.objects.get_or_create(
                email=email,
                defaults={
                    'username': 'admin',
                    'first_name': 'Admin',
                    'last_name': 'User',
                    'is_staff': True,
                    'is_superuser': True,
                    'is_active': True,
                    'is_email_verified': True,
                }
            )
            
            if created:
                admin_user.set_password(password)
                admin_user.save()
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Admin user created: {email}')
                )
            else:
                # Update password if user exists
                admin_user.set_password(password)
                admin_user.is_staff = True
                admin_user.is_superuser = True
                admin_user.is_active = True
                admin_user.save()
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Admin user updated: {email}')
                )

            self.stdout.write(
                self.style.SUCCESS(
                    f'\n🎉 Admin panel ready!\n'
                    f'URL: http://localhost:8000/admin/\n'
                    f'Email: {email}\n'
                    f'Password: {password}\n'
                )
            )