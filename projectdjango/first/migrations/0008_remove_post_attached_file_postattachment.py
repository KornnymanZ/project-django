import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('first', '0007_post'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='attached_file',
        ),
        migrations.CreateModel(
            name='PostAttachment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='team_posts/')),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attachments', to='first.post')),
            ],
        ),
    ]
