from django.db import models

class SchoolClient(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True) # e.g. 'bbc'
    db_name = models.CharField(max_length=100, unique=True) # e.g. 'bbc_school.sqlite3'
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
