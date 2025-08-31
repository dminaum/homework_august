from rest_framework.permissions import BasePermission

class IsModer(BasePermission):
    def has_permission(self, request, view):
        u = request.user
        return bool(u and u.is_authenticated and u.groups.filter(name='moderators').exists())

class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return hasattr(obj, 'owner_id') and obj.owner_id == request.user.id
