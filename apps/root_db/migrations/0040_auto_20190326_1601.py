# Generated by Django 2.1.1 on 2019-03-26 16:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('root_db', '0039_accountedcompany_last_update'),
    ]

    operations = [
        migrations.AddField(
            model_name='department',
            name='dcms_org_code_cp',
            field=models.CharField(blank=True, max_length=16, null=True, verbose_name='地区机构编号'),
        ),
        migrations.AddField(
            model_name='department',
            name='dcms_org_code_cs',
            field=models.CharField(blank=True, max_length=16, null=True, verbose_name='个人机构编号'),
        ),
        migrations.AddField(
            model_name='department',
            name='dcms_org_code_sme',
            field=models.CharField(blank=True, max_length=16, null=True, verbose_name='小微机构编号'),
        ),
    ]
