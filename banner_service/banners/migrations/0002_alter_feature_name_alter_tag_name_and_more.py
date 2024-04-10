# Generated by Django 4.2.11 on 2024-04-10 15:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('banners', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feature',
            name='name',
            field=models.CharField(db_index=True, max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='tag',
            name='name',
            field=models.CharField(db_index=True, max_length=255, unique=True),
        ),
        migrations.AddIndex(
            model_name='bannertag',
            index=models.Index(fields=['tag', 'feature'], name='banners_ban_tag_id_83bbf7_idx'),
        ),
    ]
