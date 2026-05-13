from rest_framework import permissions

class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and 
                    hasattr(request.user, 'profile') and request.user.profile.role == 'ADMIN')

class IsStandardOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        
        role = getattr(request.user.profile, 'role', 'UNASSIGNED')
        return role in ['ADMIN', 'STANDARD']
