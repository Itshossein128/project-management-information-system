import uuid
from typing import ClassVar

from django.core.exceptions import ObjectDoesNotExist
from django.db import models


class UUIDModel(models.Model):
    objects: ClassVar[models.Manager]
    DoesNotExist: type[ObjectDoesNotExist]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True
