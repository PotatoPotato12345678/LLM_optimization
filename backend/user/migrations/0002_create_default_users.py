from django.db import migrations
from django.contrib.auth.hashers import make_password

def create_default_users(apps, schema_editor):
    User = apps.get_model("user", "User")  # historical model

    debugUsers = [
        {"username": "レオ", "password": "e_1" },
        {"username": "タム", "password": "e_2" },
        {"username": "キム", "password": "e_3" },
        {"username": "とうま", "password": "e_4" },
    ]
    # Create 5 employees
    for user in debugUsers:
        username = user["username"]
        password = user["password"]
        if not User.objects.filter(username=username).exists():
            user = User(username=username, is_manager=False)
            user.password = make_password(password)
            user.save()

    # Create 1 manager
    if not User.objects.filter(username="マネージャー").exists():
        manager = User(username="マネージャー", is_manager=True)
        manager.password = make_password("m_1")
        manager.save()

    # Create superuser (admin)
    if not User.objects.filter(username="admin").exists():
        admin = User(username="admin", email="admin@admin.com", is_staff=True, is_superuser=True)
        admin.password = make_password("admin")
        admin.save()


def delete_default_users(apps, schema_editor):
    User = apps.get_model("user", "User")
    User.objects.filter(username__in=[
        "レオ", "タム", "キム", "とうま", "マネージャー", "admin"
    ]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("user", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_default_users, delete_default_users),
    ]
