# Generated by Django 2.1.1 on 2019-03-12 16:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scraper', '0027_auto_20190312_1626'),
    ]

    operations = [
        migrations.AlterField(
            model_name='luledger',
            name='loan_demand',
            field=models.ManyToManyField(to='deposit_and_credit.LoanDemand', verbose_name='贷款需求'),
        ),
    ]