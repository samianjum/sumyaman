from ..models import Student

class HierarchyService:
    @staticmethod
    def build():
        # Dinamic hierarchy based on existing students
        tree = {}
        wings = Student.objects.values_list('wing', flat=True).distinct()
        for wing in wings:
            tree[wing] = {}
            classes = Student.objects.filter(wing=wing).values_list('student_class', flat=True).distinct().order_by('student_class')
            for cls in classes:
                sections = Student.objects.filter(wing=wing, student_class=cls).values_list('student_section', flat=True).distinct()
                tree[wing][cls] = list(sections)
        return tree
