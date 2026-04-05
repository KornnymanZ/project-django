import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('first', '0006_appuser_sid_alter_appuser_email'),
    ]

    operations = [
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('body', models.TextField()),
                ('attached_file', models.FileField(blank=True, null=True, upload_to='team_posts/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='first.appuser')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='posts', to='first.team')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
