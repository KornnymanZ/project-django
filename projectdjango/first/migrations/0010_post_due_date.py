from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('first', '0009_comment_commentattachment'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='due_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
