from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('first', '0002_alter_member_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appuser',
            name='email',
            field=models.EmailField(max_length=254, unique=True, verbose_name='User Email'),
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Team Name')),
                ('groupmembers', models.ManyToManyField(to='first.appuser')),
            ],
        ),
    ]
