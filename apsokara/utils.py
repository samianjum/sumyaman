from datetime import date
from .models import AcademicSession

def is_promotion_allowed():
    try:
        current_session = AcademicSession.objects.get(is_current=True)
        today = date.today()
        if current_session.promotion_start and current_session.promotion_end:
            return current_session.promotion_start <= today <= current_session.promotion_end
        return False
    except AcademicSession.DoesNotExist:
        return False
