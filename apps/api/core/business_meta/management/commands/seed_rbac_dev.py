"""
Development seed: auth groups, sample businesses, job positions, users, assignments.
Run: python manage.py seed_rbac_dev

Default dev logins (password: devpass123):
- +10000000001 — admin
- +10000000002 — hr
- +10000000003 — visitor (read-only on unsafe routes)
- +10000000004 — worker (no admin groups)
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from django.db import transaction

from business_meta.models import (
    AssignmentStatus,
    Business,
    BusinessJobPosition,
    UserBusinessAssignment,
    WageType,
)

User = get_user_model()

# Global variable GROUPS
GROUPS = [
    "admin",
    "hr",
    "manager",
    "visitor",
    "business-setup",
    "engineer",
    "accountant",
]

# Global variable DEV_PASSWORD
DEV_PASSWORD = "devpass123"


@transaction.atomic
# Function to handle run seed
def run_seed():
    for name in GROUPS:
        Group.objects.get_or_create(name=name)

    u_admin, _ = User.objects.get_or_create(
        phone_number="+10000000001",
        defaults={"first_name": "Admin", "last_name": "User"},
    )
    u_hr, _ = User.objects.get_or_create(
        phone_number="+10000000002",
        defaults={"first_name": "HR", "last_name": "User"},
    )
    u_visitor, _ = User.objects.get_or_create(
        phone_number="+10000000003",
        defaults={"first_name": "Visitor", "last_name": "User"},
    )
    u_worker, _ = User.objects.get_or_create(
        phone_number="+10000000004",
        defaults={"first_name": "Worker", "last_name": "User"},
    )
    for u in (u_admin, u_hr, u_visitor, u_worker):
        u.set_password(DEV_PASSWORD)
        u.save()

    u_admin.groups.set([Group.objects.get(name="admin")])
    u_hr.groups.set([Group.objects.get(name="hr")])
    u_visitor.groups.set([Group.objects.get(name="visitor")])
    u_worker.groups.clear()

    b1, _ = Business.objects.get_or_create(
        slug="acme",
        defaults={"name": "Acme Construction"},
    )
    b2, _ = Business.objects.get_or_create(
        slug="buildco",
        defaults={"name": "BuildCo"},
    )

    for b in (b1, b2):
        for slug, label, ordering in (
            ("electrician", "Electrician", 0),
            ("worker", "Worker", 1),
            ("supervisor", "Supervisor", 2),
            ("plumber", "Plumber", 3),
        ):
            BusinessJobPosition.objects.get_or_create(
                business=b,
                slug=slug,
                defaults={"label": label, "ordering": ordering},
            )

    jp_e_b1 = BusinessJobPosition.objects.get(business=b1, slug="electrician")
    jp_w_b1 = BusinessJobPosition.objects.get(business=b1, slug="worker")
    jp_s_b2 = BusinessJobPosition.objects.get(business=b2, slug="supervisor")

    if not UserBusinessAssignment.objects.filter(user=u_worker, business=b1).exists():
        UserBusinessAssignment.objects.create(
            user=u_worker,
            business=b1,
            job_position=jp_e_b1,
            wage=Decimal("45.00"),
            wage_type=WageType.HOURLY,
            weekly_total=Decimal("40"),
            monthly_total=Decimal("160"),
            tools=["drill", "multimeter"],
            status=AssignmentStatus.ACTIVE,
        )
    if not UserBusinessAssignment.objects.filter(user=u_hr, business=b1).exists():
        UserBusinessAssignment.objects.create(
            user=u_hr,
            business=b1,
            job_position=jp_w_b1,
            wage=Decimal("30.00"),
            wage_type=WageType.HOURLY,
            weekly_total=Decimal("20"),
            monthly_total=Decimal("80"),
            tools=[],
            status=AssignmentStatus.ACTIVE,
        )
    if not UserBusinessAssignment.objects.filter(user=u_worker, business=b2).exists():
        UserBusinessAssignment.objects.create(
            user=u_worker,
            business=b2,
            job_position=jp_s_b2,
            wage=Decimal("5000.00"),
            wage_type=WageType.MONTHLY,
            weekly_total=Decimal("0"),
            monthly_total=Decimal("160"),
            tools=["laptop"],
            status=AssignmentStatus.SUSPENDED,
        )


# Class representing Command
class Command(BaseCommand):
    help = "Seed development RBAC: groups, businesses, job positions, users, assignments. Password: devpass123"

    # Function to handle handle
    def handle(self, *args, **options):
        run_seed()
        self.stdout.write(
            self.style.SUCCESS(
                "Seeded groups, +10000000001 (admin), +10000000002 (hr), "
                "+10000000003 (visitor), +10000000004 (worker). Password: devpass123"
            )
        )
