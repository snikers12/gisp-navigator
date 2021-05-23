from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse


class RemoveDeleteActionAdminMixin:
    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        # https://docs.djangoproject.com/en/1.11/ref/contrib/admin/actions/#conditionally-enabling-or-disabling-actions  # noqa
        # This method removes the delete action from this admin page.
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


class SingletonAdmin(admin.ModelAdmin):

    def get_admin_url(self, url, object_id=None):
        opts = self.model._meta
        url = "admin:%s_%s_%s" % (opts.app_label, opts.object_name.lower(), url)
        args = ()
        if object_id is not None:
            args = (object_id,)
        return reverse(url, args=args)

    def add_view(self, *args, **kwargs):
        instance = self.model.load()
        return redirect(self.get_admin_url("change", instance.id))

    def changelist_view(self, *args, **kwargs):
        instance = self.model.load()
        return redirect(self.get_admin_url("change", instance.id))

    def has_delete_permission(self, request, obj=None):
        return False
