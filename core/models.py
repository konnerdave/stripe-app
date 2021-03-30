from django.db import models


class NamedModel(models.Model):
    """
    An abstract base model that provides a mandatory ``name`` field.
    """

    name = models.CharField(("name"), max_length=100)

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.name}"


class TimeStampedModel(models.Model):
    """
    An abstract base model that provides self-updating
    ``created_at`` and ``updated_at`` fields.
    """

    created_at = models.DateTimeField(
        auto_now_add=True,
        blank=True,
        db_index=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        blank=True,
    )

    class Meta:
        abstract = True
