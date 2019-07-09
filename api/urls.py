from rest_framework_nested import routers

from .views import (
    IMUserCreateAPIView,
    IMUserListAPIView,
    IMUserDetailAPIView,
    IMUserUpdateAPIView,
    IMUserDeleteAPIView,
    IMGroupCreateAPIView,
    IMGroupListAPIView,
    IMGroupDetailAPIView,
    IMGroupUpdateAPIView,
    IMGroupDeleteAPIView,
    IMRoleCreateAPIView,
    IMRoleListAPIView,
    IMRoleDetailAPIView,
    IMRoleUpdateAPIView,
    IMRoleDeleteAPIView
)

from .views import IMUserViewSet,IMGroupViewSet, IMRoleViewSet

from django.urls import include, path
app_name = 'applicationManager-api'

# ------ Identity Manager Router Configuration-----------------------------------------------------------
# Router conf. gives us the luxury to not define paths manually, instead router enables all CRUD paths with accordance
# to a predifined path structure.

# identitymanager_router = routers.DefaultRouter()
# identitymanager_router.register('imusers', IMUserViewSet)
# identitymanager_router.register('imgroups', IMGroupViewSet)
# identitymanager_router.register('imroles', IMRoleViewSet)
#
# imgroups_router = routers.NestedSimpleRouter(identitymanager_router, 'imgroups', lookup='imgroup')
# imgroups_router.register('memberusers', IMGroupMemberUserViewSet, base_name='imgroup-memberusers')
# imgroups_router.register('membergroups', IMGroupMemberGroupViewSet, base_name='imgroup-membergroups')
#
# imroles_router = routers.NestedSimpleRouter(identitymanager_router, 'imroles', lookup='imrole')
# imroles_router.register('permissions', IMRolePermissionViewSet, base_name='imrole-permissions')
# imroles_router.register('assignedusers', IMRoleAssignedUserViewSet, base_name='imrole-assignedusers')
# imroles_router.register('assignedgroups', IMRoleAssignedGroupViewSet, base_name='imrole-assignedgroups')

urlpatterns = [

    # --------- Router Based Paths ------------
    # path('', include(identitymanager_router.urls)),

    # --------- Custom paths -------------------
    # Following paths are just for imuser API
    path('imuser/', IMUserListAPIView.as_view(), name='imuser-list'),
    path('imuser/create/', IMUserCreateAPIView.as_view(), name='imuser-create'),
    path('imuser/<int:pk>/', IMUserDetailAPIView.as_view(), name="imuser-detail"),
    path('imuser/<int:pk>/edit/', IMUserUpdateAPIView.as_view(), name="imuser-edit"),
    path('imuser/<int:pk>/delete/', IMUserDeleteAPIView.as_view(), name="imuser-delete"),

    # Following paths are just for imgroup API
    path('imgroup/', IMGroupListAPIView.as_view(), name='imgroup-list'),
    path('imgroup/create/', IMGroupCreateAPIView.as_view(), name='imgroup-create'),
    path('imgroup/<int:pk>/', IMGroupDetailAPIView.as_view(), name="imgroup-detail"),
    path('imgroup/<int:pk>/edit/', IMGroupUpdateAPIView.as_view(), name="imgroup-edit"),
    path('imgroup/<int:pk>/delete/', IMGroupDeleteAPIView.as_view(), name="imgroup-delete"),

    # Following paths are just for imrole API
    path('imrole/', IMRoleListAPIView.as_view(), name='imrole-list'),
    path('imrole/create/', IMRoleCreateAPIView.as_view(), name='imrole-create'),
    path('imrole/<int:pk>/', IMRoleDetailAPIView.as_view(), name="imrole-detail"),
    path('imrole/<int:pk>/edit/', IMRoleUpdateAPIView.as_view(), name="imrole-edit"),
    path('imrole/<int:pk>/delete/', IMRoleDeleteAPIView.as_view(), name="imrole-delete"),
]
