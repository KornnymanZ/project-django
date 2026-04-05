from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('first', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='AppUser',
            name='name',
            field=models.CharField(max_length=70),
        ),
    ]
