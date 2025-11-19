from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('matrix_web', '0002_add_16port_features'),
    ]
    
    operations = [
        migrations.AddField(
            model_name='profile',
            name='order',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]
