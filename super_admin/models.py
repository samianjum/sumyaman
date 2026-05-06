from django.db import models

class SchoolClient(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    SCHOOL_TYPES = [('co-ed', 'Co-Education'), ('wing-based', 'Wing Based (Boys/Girls)')]
    school_type = models.CharField(max_length=20, choices=SCHOOL_TYPES, default='co-ed')
    logo = models.ImageField(upload_to="school_logos/", null=True, blank=True) # e.g. 'bbc'
    db_name = models.CharField(max_length=100, unique=True) # e.g. 'bbc_school.sqlite3'
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
