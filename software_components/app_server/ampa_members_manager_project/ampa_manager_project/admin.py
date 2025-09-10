from django.conf import settings
from django.contrib import admin
from django.contrib.admin.apps import AdminConfig
from django.urls import reverse


class MenuGroup:
    def __init__(self, app_label: str, app_url: str, name: str):
        self.app_label = app_label
        self.app_url = app_url
        self.name = name
        self.models = []

    def to_dict(self):
        return {
            'app_label': self.app_label,
            'app_url': self.app_url,
            'name': self.name,
            'models': self.models
        }


class MenuGroupLink:
    def __init__(self, name: str, admin_url: str):
        self.name = name
        self.object_name = name
        self.admin_url = admin_url
        self.add_url = None
        self.view_only = True

    def to_dict(self):
        return {
            'name': self.name,
            'object_name': self.object_name,
            'admin_url': self.admin_url,
            'add_url': self.add_url,
            'view_only': self.view_only
        }


class CustomAdminSite(admin.AdminSite):
    def index(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['menu'] = self.get_custom_app_list()
        extra_context['show_changelinks'] = False
        return super().index(request, extra_context=extra_context)

    def each_context(self, request):
        context = super().each_context(request)
        context['menu'] = self.get_custom_app_list()
        from ampa_manager.academic_course.models.active_course import ActiveCourse
        context['active_course'] = str(ActiveCourse.load())
        return context

    @staticmethod
    def get_custom_app_list():
        app_list = []

        for admin_group in settings.ADMIN_MENU:
            group_label = admin_group['group_label']
            menu_app = MenuGroup(app_label=group_label, app_url='#', name=group_label)

            for group_link in admin_group['links']:
                link_app = group_link['app']
                link_label = group_link['label']
                link_type = group_link['type']
                if link_type == 'model':
                    link_model = group_link['model']
                    link_url = reverse('admin:%s_%s_changelist' % (link_app, link_model))
                elif link_type == 'view':
                    link_view = group_link['view']
                    link_url = reverse(link_view)
                else:
                    continue

                menu_app.models.append(
                    MenuGroupLink(
                        name=link_label,
                        admin_url=link_url
                    ).to_dict()
                )
            app_list.append(menu_app.to_dict())

        return app_list


class CustomAdminConfig(AdminConfig):
    default_site = "ampa_manager_project.admin.CustomAdminSite"
