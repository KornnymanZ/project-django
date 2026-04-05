from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('first', '0011_notification'),
    ]

    operations = [
        migrations.AddField(
            model_name='appuser',
            name='profile_picture',
            field=models.ImageField(blank=True, null=True, upload_to='profile_pics/'),
        ),
    ]
