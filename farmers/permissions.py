from rest_framework.permissions import BasePermission


class IsFarmerOwner(BasePermission):
    """
    Only allows access if the requesting user is the farmer
    who owns the produce listing.
    """
    message = 'You can only modify your own produce listings.'

    def has_object_permission(self, request, view, obj):
        return obj.farmer == request.user
