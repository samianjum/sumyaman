from django import forms
from django.forms import inlineformset_factory
from .models import Student, Teacher, Subject, SubjectAssignment
from django.core.exceptions import ValidationError

CLASS_CHOICES = [('', 'Select Class')] + [(str(i), str(i)) for i in range(1, 11)]

RELIGION_CHOICES = [('', 'Select Religion'), ('Islam', 'Islam'), ('Christianity', 'Christianity'), ('Other', 'Other')]
PROVINCE_CHOICES = [('', 'Select Province'), ('Punjab', 'Punjab'), ('Sindh', 'Sindh'), ('KPK', 'KPK'), ('Balochistan', 'Balochistan'), ('Gilgit', 'Gilgit')]
SECTION_CHOICES = [('', 'Select Section'), ('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')]

class StudentForm(forms.ModelForm):
    student_class = forms.ChoiceField(choices=CLASS_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    student_section = forms.ChoiceField(choices=SECTION_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    religion = forms.ChoiceField(choices=RELIGION_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    province = forms.ChoiceField(choices=PROVINCE_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    nationality = forms.CharField(initial='Pakistani', widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Student
        fields = '__all__'
        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'address': forms.Textarea(attrs={'rows': 1, 'placeholder': 'Full Address...', 'class': 'form-control'}),
        }

    def clean_b_form(self):
        b_form = self.cleaned_data.get('b_form')
        if not b_form: return b_form
        s_exists = Student.objects.filter(b_form=b_form).exclude(pk=self.instance.pk).first()
        if s_exists:
            details = f"{s_exists.full_name} (Class: {s_exists.student_class}-{s_exists.student_section}, Wing: {s_exists.wing})"
            raise ValidationError(f"Already exists: {details}")
        return b_form


    def clean(self):
        cleaned_data = super().clean()
        # Essential fields validation
        required = ['full_name', 'father_name', 'b_form', 'roll_number', 'student_class', 'student_section', 'nationality', 'religion']
        for field in required:
            if not cleaned_data.get(field):
                self.add_error(field, "This field is required.")
        return cleaned_data

    def __init__(self, *args, **kwargs):
        self.school_type = kwargs.pop('school_type', 'co-ed')
        super().__init__(*args, **kwargs)
        if self.school_type == 'co-ed':
            if 'wing' in self.fields:
                self.fields['wing'].widget = forms.HiddenInput()
                self.fields['wing'].required = False
                self.fields['wing'].initial = 'None'
            if 'assigned_wing' in self.fields:
                self.fields['assigned_wing'].widget = forms.HiddenInput()
                self.fields['assigned_wing'].required = False
                self.fields['assigned_wing'].initial = 'None'
        for name, field in self.fields.items():
            if not isinstance(field.widget, (forms.Select, forms.DateInput, forms.Textarea)):
                field.widget.attrs.update({'class': 'form-control'})


class TeacherForm(forms.ModelForm):
    assigned_class = forms.ChoiceField(choices=CLASS_CHOICES, required=False)
    assigned_section = forms.ChoiceField(choices=SECTION_CHOICES, required=False)

    class Meta:
        model = Teacher
        fields = '__all__'
        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 1, 'placeholder': 'Residential Address...'}),
        }

    def clean_b_form(self):
        b_form = self.cleaned_data.get('b_form')
        if not b_form: return b_form
        s_exists = Student.objects.filter(b_form=b_form).exclude(pk=self.instance.pk).first()
        if s_exists:
            details = f"{s_exists.full_name} (Class: {s_exists.student_class}-{s_exists.student_section}, Wing: {s_exists.wing})"
            raise ValidationError(f"Already exists: {details}")
        return b_form

    def clean_cnic(self):
        cnic = self.cleaned_data.get('cnic')
        # Check Teachers
        t_exists = Teacher.objects.filter(cnic=cnic).exclude(pk=self.instance.pk).first()
        if t_exists:
            raise ValidationError(f"Conflict: Teacher '{t_exists.full_name}' is already registered with this CNIC.")
        # Check Students
        s_exists = Student.objects.filter(b_form=cnic).first()
        if s_exists:
            raise ValidationError(f"Conflict: Student '{s_exists.full_name}' is already registered with this B-Form/CNIC.")
        return cnic

    def clean(self):
        cleaned_data = super().clean()
        is_class_teacher = cleaned_data.get('is_class_teacher')
        a_class = cleaned_data.get('assigned_class')
        section = cleaned_data.get('assigned_section')
        wing = cleaned_data.get('assigned_wing')

        if is_class_teacher:
            if not a_class: self.add_error('assigned_class', "Class is required.")
            if not section: self.add_error('assigned_section', "Section is required.")
            if self.school_type == 'wing-based' and (not wing or wing == 'None'):
                self.add_error('assigned_wing', "Wing is required.")

            existing = Teacher.objects.filter(
                is_class_teacher=True,
                assigned_class=a_class,
                assigned_section=section,
                assigned_wing=wing
            ).exclude(pk=self.instance.pk).first()

            if existing:
                raise ValidationError(f"Conflict: {existing.full_name} is already the Class Teacher for {a_class}-{section} ({wing}).")
        return cleaned_data

    def __init__(self, *args, **kwargs):
        self.school_type = kwargs.pop('school_type', 'co-ed')
        super().__init__(*args, **kwargs)
        if self.school_type == 'co-ed':
            if 'wing' in self.fields:
                self.fields['wing'].widget = forms.HiddenInput()
                self.fields['wing'].required = False
                self.fields['wing'].initial = 'None'
            if 'assigned_wing' in self.fields:
                self.fields['assigned_wing'].widget = forms.HiddenInput()
                self.fields['assigned_wing'].required = False
                self.fields['assigned_wing'].initial = 'None'
        for name, field in self.fields.items():
            if name == 'is_class_teacher':
                field.widget.attrs.update({'class': 'form-check-input'})
            else:
                field.widget.attrs.update({'class': 'form-control'})



class SubjectAssignmentForm(forms.ModelForm):
    student_class = forms.ChoiceField(choices=CLASS_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    section = forms.ChoiceField(choices=SECTION_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = SubjectAssignment
        fields = ['subject', 'student_class', 'section', 'wing']

    def __init__(self, *args, **kwargs):
        self.school_type = kwargs.pop('school_type', 'co-ed')
        super().__init__(*args, **kwargs)
        if self.school_type == 'co-ed':
            self.fields['wing'].initial = 'None'
            self.fields['wing'].required = False
            self.fields['wing'].widget = forms.HiddenInput()
        else:
            self.fields['wing'].widget.attrs.update({'class': 'form-control'})

    def clean(self):
        cleaned_data = super().clean()
        wing = cleaned_data.get('wing')
        if self.school_type == 'co-ed':
            cleaned_data['wing'] = 'None'
        elif not wing:
            cleaned_data['wing'] = 'None'
        return cleaned_data
SubjectAssignmentFormSet = inlineformset_factory(
    Teacher, SubjectAssignment, form=SubjectAssignmentForm, extra=1, can_delete=True
)

# ---------- FEE FORMS ----------
from django import forms
from .models import FeeStructure, FeeRecord, PaymentTransaction

class FeeStructureForm(forms.ModelForm):
    class Meta:
        model = FeeStructure
        fields = ['student_class', 'monthly_fee']
        widgets = {
            'student_class': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 5'}),
            'monthly_fee': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

class FeeCollectionForm(forms.Form):
    student_id = forms.IntegerField(label='Student ID', widget=forms.NumberInput(attrs={'class': 'form-control'}))
    amount = forms.DecimalField(label='Amount', widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}))
    payment_mode = forms.ChoiceField(choices=PaymentTransaction.MODE_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    remarks = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}))

class FamilyPaymentForm(forms.Form):
    father_cnic = forms.CharField(label='Father CNIC / B-Form', widget=forms.TextInput(attrs={'class': 'form-control'}))
    amount = forms.DecimalField(required=False, label='Amount (leave blank to pay all pending)', widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}))
    payment_mode = forms.ChoiceField(choices=PaymentTransaction.MODE_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
