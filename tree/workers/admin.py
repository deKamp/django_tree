from django.contrib import admin

from mptt.admin import MPTTModelAdmin
from .models import Workers


admin.site.register(Workers, MPTTModelAdmin)
