from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.utils.translation import gettext_lazy as _
from .models import User

# Formulaire personnalisé pour la modification d'utilisateur
class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        fields = '__all__'
        exclude = ('username',)  # Exclure explicitement le champ username

# Formulaire personnalisé pour la création d'utilisateur
class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('email', 'first_name', 'last_name', 'role')
        exclude = ('username',)  # Exclure explicitement le champ username

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Supprimer la validation du username
        if 'username' in self.fields:
            del self.fields['username']

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_active', 'is_staff')
    list_filter = ('role', 'is_active', 'is_staff', 'is_superuser', 'created_at')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'last_login')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Informations personnelles'), {'fields': ('first_name', 'last_name', 'role')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Dates importantes'), {'fields': ('last_login', 'created_at', 'updated_at')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'role', 'password1', 'password2'),
        }),
    )

    # Surcharger les méthodes pour éviter toute référence à username
    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        # Nettoyer les fieldsets de toute référence à username
        for fieldset in fieldsets:
            if 'fields' in fieldset[1]:
                fields = list(fieldset[1]['fields'])
                if 'username' in fields:
                    fields.remove('username')
                fieldset[1]['fields'] = tuple(fields)
        return fieldsets

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Supprimer le champ username s'il existe
        if 'username' in form.base_fields:
            del form.base_fields['username']
        return form