from rest_framework.permissions import BasePermission


class HasRole(BasePermission):

    allowed_roles = []

    def has_permission(self, request, view):

        role = getattr(
            request.user,
            "role",
            None
        ).lower()

        return (
            request.user.is_authenticated
            and role in self.allowed_roles
        )


class IsClient(HasRole):
    allowed_roles = ["client"]


class IsFreelancer(HasRole):
    allowed_roles = ["freelancer"]


class IsAdmin(HasRole):
    allowed_roles = ["labora_admin"]