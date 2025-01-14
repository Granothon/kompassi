from django.contrib import admin

from .models import Form, Response, Survey


class FormAdmin(admin.ModelAdmin):
    model = Form
    list_display = ("event", "slug", "title")
    list_filter = ("event",)
    search_fields = ("slug", "title")


class ResponseAdmin(admin.ModelAdmin):
    model = Response
    list_display = ("created_at", "form", "created_by")
    list_filter = ("form__event", "form")
    readonly_fields = ("form", "form_data", "created_by", "created_at", "updated_at")

    def has_add_permission(self, *args, **kwargs):
        return False


class SurveyFormInline(admin.TabularInline):
    model = Survey.languages.through
    extra = 1


class SurveyAdmin(admin.ModelAdmin):
    model = Survey
    list_display = ("event", "slug", "admin_is_active")
    list_filter = ("event",)
    fields = ("event", "slug", "active_from", "active_until")
    inlines = (SurveyFormInline,)


admin.site.register(Form, FormAdmin)
admin.site.register(Response, ResponseAdmin)
admin.site.register(Survey, SurveyAdmin)
