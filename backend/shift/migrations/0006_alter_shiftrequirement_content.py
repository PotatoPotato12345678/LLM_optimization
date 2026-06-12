from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shift', '0005_alter_managerrequirement_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shiftrequirement',
            name='content',
            field=models.TextField(blank=True),
        ),
    ]
