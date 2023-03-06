from django.db import migrations, transaction


def create_profiles(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    Profile = apps.get_model('chat', 'Profile')

    with transaction.atomic():
        for user in User.objects.all():
            profile, created = Profile.objects.get_or_create(user=user)
            if created:
                profile.save()


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0006_alter_profile_user'),
    ]

    operations = [
        migrations.RunPython(create_profiles),
    ]
