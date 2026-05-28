import threading
from django.conf import settings

_thread_locals = threading.local()

def set_current_db(db_name):
    _thread_locals.db_name = db_name

def get_current_db():
    return getattr(_thread_locals, 'db_name', 'default')

class TenantRouter:
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'super_admin':
            return 'default'
        return get_current_db()

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'super_admin':
            return 'default'
        return get_current_db()

    def allow_relation(self, obj1, obj2, **hints):
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        # Always allow migrations on the specific DB being targeted
        if db == 'default':
            return app_label != 'apsokara'

        # If it's a tenant DB, allow everything except super_admin
        return app_label != 'super_admin'
