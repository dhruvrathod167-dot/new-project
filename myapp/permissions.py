from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Allow admins to perform any action.
    Others can only perform safe (read-only) operations.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


class IsStaffMember(permissions.BasePermission):
    """
    Allow only staff members to access.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_staff


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Allow owners to edit their own objects.
    Others can only read.
    """
    def has_object_permission(self, request, view, obj):
        # Allow safe methods to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Check if user is the owner
        return obj.user == request.user or request.user.is_staff


class CanManageProducts(permissions.BasePermission):
    """
    Allow only staff members to create, update, or delete products.
    Everyone can view.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


class CanManageJournal(permissions.BasePermission):
    """
    Allow only staff members to create, update, or delete journal articles.
    Everyone can view published articles.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


class CanModerateComments(permissions.BasePermission):
    """
    Allow staff to approve/delete comments.
    Users can create their own comments.
    """
    def has_permission(self, request, view):
        # Anyone can create comments on GET (list)
        if request.method in permissions.SAFE_METHODS:
            return True
        # Only staff can modify
        if request.method in ['DELETE', 'PATCH']:
            return request.user and request.user.is_staff
        # Users can create comments
        return request.user and request.user.is_authenticated
