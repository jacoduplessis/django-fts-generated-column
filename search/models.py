from django.db import models
from django.contrib.postgres.search import SearchVectorField
from django.contrib.postgres.indexes import GinIndex
from django.db.models.expressions import F


from psycopg2.extensions import register_adapter, AsIs


class PostgresDefaultValueType:
    pass


class DelegatedSearchVectorField(SearchVectorField):
    def get_prep_value(self, value):
        return value or PostgresDefaultValueType()


register_adapter(PostgresDefaultValueType, lambda _: AsIs("DEFAULT"))


class Author(models.Model):
    name = models.CharField(max_length=200, blank=True)


class Book(models.Model):
    title = models.CharField(max_length=1000, blank=True)
    description = models.TextField(blank=True)
    author = models.ForeignKey(Author, on_delete=models.SET_NULL, null=True, blank=True)
    search_vector = DelegatedSearchVectorField(null=True, editable=False)

    def get_deferred_fields(self):
        fields = super().get_deferred_fields()
        fields.add("search_vector")
        return fields

    class Meta:
        indexes = [
            GinIndex(
                fields=["search_vector"],
                name="search_vector_idx",
            ),
        ]
