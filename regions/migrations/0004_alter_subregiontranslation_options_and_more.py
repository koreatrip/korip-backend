# Generated by Django 5.2.3 on 2025-07-20 16:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('regions', '0003_subregiontranslation_features'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='subregiontranslation',
            options={'verbose_name': '지역구 번역', 'verbose_name_plural': '지역구 번역'},
        ),
        migrations.AlterField(
            model_name='regiontranslation',
            name='lang',
            field=models.CharField(choices=[('ko', '한국어'), ('en', 'English'), ('jp', '日本語'), ('cn', '中文')], max_length=5, verbose_name='언어 코드'),
        ),
        migrations.AlterField(
            model_name='subregiontranslation',
            name='lang',
            field=models.CharField(choices=[('ko', '한국어'), ('en', 'English'), ('jp', '日本語'), ('cn', '中文')], max_length=5, verbose_name='언어 코드'),
        ),
    ]
