from django.db import migrations
from django.contrib.auth.hashers import make_password

def create_default_users(apps, schema_editor):
    User = apps.get_model("user", "User")  # historical model

    # Create 5 employees
    for i in range(1, 6):
        username = f"employee_{i}"
        password = f"password_e_{i}"
        if not User.objects.filter(username=username).exists():
            user = User(username=username, is_manager=False)
            user.password = make_password(password)
            user.save()

    # Create 1 manager
    if not User.objects.filter(username="manager_1").exists():
        manager = User(username="manager_1", is_manager=True)
        manager.password = make_password("password_m_1")
        manager.save()

    # Create superuser (admin)
    if not User.objects.filter(username="admin").exists():
        admin = User(username="admin", email="admin@admin.com", is_staff=True, is_superuser=True)
        admin.password = make_password("admin")
        admin.save()


def delete_default_users(apps, schema_editor):
    User = apps.get_model("user", "User")
    User.objects.filter(username__in=[
        "employee_1", "employee_2", "employee_3", "employee_4", "employee_5", "manager_1", "admin"
    ]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("user", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_default_users, delete_default_users),
    ]
