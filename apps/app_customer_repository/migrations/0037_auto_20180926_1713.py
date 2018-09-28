# Generated by Django 2.1.1 on 2018-09-26 17:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_customer_repository', '0036_auto_20180924_1644'),
    ]

    operations = [
        migrations.CreateModel(
            name='PretrialDocumentWaitForMeeting',
            fields=[
            ],
            options={
                'verbose_name': '待预审项目',
                'verbose_name_plural': '待预审项目',
                'proxy': True,
                'indexes': [],
            },
            bases=('app_customer_repository.pretrialdocument',),
        ),
        migrations.AlterField(
            model_name='pretrialdocument',
            name='document_file',
            field=models.FileField(blank=True, null=True, upload_to='pre_doc/%Y/%m', verbose_name='预审表'),
        ),
    ]