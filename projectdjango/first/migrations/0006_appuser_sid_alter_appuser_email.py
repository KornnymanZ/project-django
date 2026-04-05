from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('first', '0005_alter_appuser_user_alter_team_groupmembers'),
    ]

    operations = [
        migrations.AddField(
            model_name='appuser',
            name='sid',
            field=models.CharField(max_length=50, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='appuser',
            name='email',
            field=models.EmailField(max_length=254, unique=True),
        ),
    ]
