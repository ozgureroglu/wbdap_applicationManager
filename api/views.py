from django.contrib.auth.models import Permission
from django.shortcuts import render

# Create your views here.
from rest_framework import filters, viewsets, status
from rest_framework.generics import (
    CreateAPIView,
    ListAPIView,
    RetrieveAPIView,
    UpdateAPIView,
    RetrieveUpdateAPIView,
    DestroyAPIView
)
from rest_framework.response import Response


from applicationManager.models import DjangoProject, Application
from .serializers import (
    ApplicationCreateSerializer,
    ApplicationListSerializer,
    ApplicationDetailSerializer,
    DjangoProjectCreateSerializer,
    DjangoProjectListSerializer,
    DjangoProjectDetailSerializer,
)

from projectCore.datatable_viewset import ModifiedViewSet
import logging

logger = logging.getLogger("api.views")


# Instead of using ViewSets (below tis section) we can create all CRUD views seperately and manualy :
# these views are accessed by Router Based Paths in api.urls.py instead of routers which provide the
# necessary paths automatically (which enables us to access views in a predefined path structrue)
# ----------- IMUSER ------------------------------

class ApplicationCreateAPIView(CreateAPIView):
    queryset = Application.objects.all()
    serializer_class = ApplicationCreateSerializer


class ApplicationListAPIView(ListAPIView):
    queryset = Application.objects.all()
    serializer_class = ApplicationListSerializer


class ApplicationDetailAPIView(RetrieveAPIView):
    queryset = Application.objects.all()
    serializer_class = ApplicationDetailSerializer
    # Asagidakileri degistirince urls icinde de abc pattern ile search yapilmasi gerekir
    # lookup_field = 'slug'
    # lookup_url_kwarg = 'abc'


class ApplicationUpdateAPIView(RetrieveUpdateAPIView):
    queryset = Application.objects.all()
    serializer_class = ApplicationDetailSerializer
    # Asagidakileri degistirince urls icinde de abc pattern ile search yapilmasi gerekir
    # lookup_field = 'slug'
    # lookup_url_kwarg = 'abc'


class ApplicationDeleteAPIView(DestroyAPIView):
    queryset = Application.objects.all()
    serializer_class = ApplicationDetailSerializer
    # Asagidakileri degistirince urls icinde de abc pattern ile search yapilmasi gerekir
    # lookup_field = 'slug'
    # lookup_url_kwarg = 'abc'


# ----------- IMGROUP ------------------------------

class DjangoProjectCreateAPIView(CreateAPIView):
    queryset = DjangoProject.objects.all()
    serializer_class = DjangoProjectCreateSerializer


class DjangoProjectListAPIView(ListAPIView):
    queryset = DjangoProject.objects.all()
    serializer_class = DjangoProjectListSerializer


class DjangoProjectDetailAPIView(RetrieveAPIView):
    queryset = DjangoProject.objects.all()
    serializer_class = DjangoProjectDetailSerializer
    # Asagidakileri degistirince urls icinde de abc pattern ile search yapilmasi gerekir
    # lookup_field = 'slug'
    # lookup_url_kwarg = 'abc'


class DjangoProjectUpdateAPIView(RetrieveUpdateAPIView):
    queryset = DjangoProject.objects.all()
    serializer_class = DjangoProjectDetailSerializer
    # Asagidakileri degistirince urls icinde de abc pattern ile search yapilmasi gerekir
    # lookup_field = 'slug'
    # lookup_url_kwarg = 'abc'


class DjangoProjectDeleteAPIView(DestroyAPIView):
    queryset = DjangoProject.objects.all()
    serializer_class = DjangoProjectDetailSerializer
    # Asagidakileri degistirince urls icinde de abc pattern ile search yapilmasi gerekir
    # lookup_field = 'slug'
    # lookup_url_kwarg = 'abc'


# # ----------- IMROLE ------------------------------
#
# class IMRoleCreateAPIView(CreateAPIView):
#     queryset = IMRole.objects.all()
#     serializer_class = IMRoleCreateSerializer
#
#
# class IMRoleListAPIView(ListAPIView):
#     queryset = IMRole.objects.all()
#     serializer_class = IMRoleListSerializer
#
#
# class IMRoleDetailAPIView(RetrieveAPIView):
#     queryset = IMRole.objects.all()
#     serializer_class = IMRoleDetailSerializer
#     # Asagidakileri degistirince urls icinde de abc pattern ile search yapilmasi gerekir
#     # lookup_field = 'slug'
#     # lookup_url_kwarg = 'abc'
#
#
# class IMRoleUpdateAPIView(RetrieveUpdateAPIView):
#     queryset = IMRole.objects.all()
#     serializer_class = IMRoleDetailSerializer
#     # Asagidakileri degistirince urls icinde de abc pattern ile search yapilmasi gerekir
#     # lookup_field = 'slug'
#     # lookup_url_kwarg = 'abc'
#
#
# class IMRoleDeleteAPIView(DestroyAPIView):
#     queryset = IMRole.objects.all()
#     serializer_class = IMRoleDetailSerializer
#     # Asagidakileri degistirince urls icinde de abc pattern ile search yapilmasi gerekir
#     # lookup_field = 'slug'
#     # lookup_url_kwarg = 'abc'
#
#
# # -----------------------------------------
#
# class ApplicationViewSet(ModifiedViewSet):
#     """
#     API endpoint that allows users to view existing exams.
#     This viewset automatically provides `list`, `create`, `retrieve`,
#     `update` and `destroy` actions.
#     """
#     queryset = Application.objects.all()
#     serializer_class = ApplicationListSerializer
#     filter_backends = (filters.OrderingFilter, filters.SearchFilter)
#     search_fields = ('username','first_name','last_name','email',)
#     ordering_fields = ('username','first_name','last_name','email','is_superuser','is_staff','is_active')
#
#
# class DjangoProjectViewSet(ModifiedViewSet):
#     """
#     API endpoint that allows users to view existing exams. In fact this viewset
#     allows us to do all CRUD operations on the object defined in the queryset
#     parameter.
#     """
#     queryset = DjangoProject.objects.all()
#     serializer_class = DjangoProjectSerializer
#
#     def update(self, request, *args, **kwargs):
#         resp = super().update(request)
#         return Response({'data': [resp.data]})
#
#     def create(self, request, *args, **kwargs):
#         resp = super().create(request)
#         return Response({'data': [resp.data]})
#
#
# class DjangoProjectMemberUserViewSet(viewsets.ModelViewSet):
#     serializer_class = ApplicationListSerializer
#
#     def get_queryset(self):
#         grp_id =self.kwargs['imgroup_pk']
#         grp = DjangoProject.objects.get(id=grp_id)
#         queryset = grp.memberUsers.all()
#         return queryset
#
#     # Creates the group membership record
#     def create(self, request, *args, **kwargs):
#         try:
#             imgroup=DjangoProject.objects.get(id=self.kwargs['imgroup_pk'])
#             usernames = request.data['username']
#
#             username_list = str(usernames).strip(' ').strip(',')
#             username_list = username_list.split(',')
#
#             for username in username_list:
#                 print('adding %s' % username.strip())
#                 imgroup.memberUsers.add(Application.objects.get(username= username.strip(' ')))
#
#         except Exception as e:
#             logger.fatal(e);
#             logger.fatal('unable to add user to group')
#
#         members = DjangoProject.objects.get(id=self.kwargs['imgroup_pk']).memberUsers.all()
#         serializer = self.get_serializer(members,many=True)
#         headers = self.get_success_headers(serializer.data)
#
#         return Response({'data':serializer.data})
#
#
#     # Removes the user from group
#     def destroy(self, request, *args, **kwargs):
#         print('delete')
#         print(self.kwargs)
#         DjangoProject.objects.get(id=self.kwargs['imgroup_pk']).memberUsers.remove(Application.objects.get(id=self.kwargs['pk']))
#
#         members = DjangoProject.objects.get(id=self.kwargs['imgroup_pk']).memberUsers.all()
#         serializer = self.get_serializer(members, many=True)
#         headers = self.get_success_headers(serializer.data)
#
#         return Response({'data': serializer.data})
#
#
# class DjangoProjectMemberGroupViewSet(viewsets.ModelViewSet):
#     serializer_class = DjangoProjectSerializer
#
#     def get_queryset(self):
#         grp_id =self.kwargs['imgroup_pk']
#         grp = DjangoProject.objects.get(id=grp_id)
#         queryset = grp.memberGroups.all()
#         return queryset
#
#
#  # Creates the group membership record
#     def create(self, request, *args, **kwargs):
#         try:
#             imgroup=DjangoProject.objects.get(id=self.kwargs['imgroup_pk'])
#             subgrp_names = request.data['name']
#
#             subgrp_name_list = str(subgrp_names).strip(' ').strip(',')
#             subgrp_name_list = subgrp_name_list.split(',')
#
#             for subgrp_name in subgrp_name_list:
#                 print('adding %s' % subgrp_name.strip())
#                 imgroup.memberGroups.add(DjangoProject.objects.get(name=subgrp_name.strip(' ')))
#
#         except Exception as e:
#             logger.fatal(e);
#             logger.fatal('unable to add group to group')
#
#         members = DjangoProject.objects.get(id=self.kwargs['imgroup_pk']).memberGroups.all()
#         serializer = self.get_serializer(members,many=True)
#         headers = self.get_success_headers(serializer.data)
#
#         return Response({'data': serializer.data})
#
#
#     # Removes the user from group
#     def destroy(self, request, *args, **kwargs):
#         print('delete')
#         print(self.kwargs)
#         DjangoProject.objects.get(id=self.kwargs['imgroup_pk']).memberGroups.remove(DjangoProject.objects.get(id=self.kwargs['pk']))
#
#         members = DjangoProject.objects.get(id=self.kwargs['imgroup_pk']).memberGroups.all()
#         serializer = self.get_serializer(members, many=True)
#         headers = self.get_success_headers(serializer.data)
#
#         return Response({'data': serializer.data})
#
#
# class IMRoleViewSet(viewsets.ModelViewSet):
#     """
#     API endpoint that allows users to view existing exams
#     """
#     queryset = IMRole.objects.all()
#     serializer_class = IMRoleSerializer
#
#     filter_backends = (filters.OrderingFilter, filters.SearchFilter)
#     search_fields = ('name',)
#     ordering_fields = ('name',)
#
#     def update(self, request, *args, **kwargs):
#         resp = super().update(request)
#         return Response({'data': [resp.data]})
#
#
#     def create(self, request, *args, **kwargs):
#         resp = super().create(request)
#         return Response({'data': [resp.data]})
#
#
# class IMRoleAssignedUserViewSet(viewsets.ModelViewSet):
#     serializer_class = ApplicationListSerializer
#
#     def get_queryset(self):
#         role_id =self.kwargs['imrole_pk']
#         role = IMRole.objects.get(id=role_id)
#         queryset = role.assigned_users.all()
#         return queryset
#
#     # Creates the role membership record
#     def create(self, request, *args, **kwargs):
#         try:
#             imrole=IMRole.objects.get(id=self.kwargs['imrole_pk'])
#             usernames = request.data['username']
#
#             username_list = str(usernames).strip(' ').strip(',')
#             username_list = username_list.split(',')
#
#             for username in username_list:
#                 print('adding %s' % username.strip())
#                 imrole.assigned_users.add(Application.objects.get(username= username.strip(' ')))
#
#         except Exception as e:
#             logger.fatal(e);
#             logger.fatal('unable to add user to group')
#
#         members = IMRole.objects.get(id=self.kwargs['imrole_pk']).assigned_users.all()
#         serializer = self.get_serializer(members, many=True)
#         headers = self.get_success_headers(serializer.data)
#
#         return Response({'data':serializer.data})
#
#
#     # Removes the user from group
#     def destroy(self, request, *args, **kwargs):
#
#         print(self.kwargs)
#         IMRole.objects.get(id=self.kwargs['imrole_pk']).assigned_users.remove(Application.objects.get(id=self.kwargs['pk']))
#
#         users = IMRole.objects.get(id=self.kwargs['imrole_pk']).assigned_users.all()
#         serializer = self.get_serializer(users, many=True)
#         headers = self.get_success_headers(serializer.data)
#
#         return Response({'data': serializer.data})
#
#
# class IMRoleAssignedGroupViewSet(viewsets.ModelViewSet):
#     serializer_class = DjangoProjectSerializer
#
#     def get_queryset(self):
#         role_id =self.kwargs['imrole_pk']
#         role = IMRole.objects.get(id=role_id)
#         queryset = role.assigned_groups.all()
#         return queryset
#
#
#  # Creates the group membership record
#     def create(self, request, *args, **kwargs):
#         try:
#             imrole=IMRole.objects.get(id=self.kwargs['imrole_pk'])
#             subgrp_names = request.data['name']
#
#             subgrp_name_list = str(subgrp_names).strip(' ').strip(',')
#             subgrp_name_list = subgrp_name_list.split(',')
#
#             for subgrp_name in subgrp_name_list:
#                 print('adding %s' % subgrp_name.strip())
#                 imrole.assigned_groups.add(DjangoProject.objects.get(name=subgrp_name.strip(' ')))
#
#         except Exception as e:
#             logger.fatal(e);
#             logger.fatal('unable to add group to group')
#
#         groups = IMRole.objects.get(id=self.kwargs['imrole_pk']).assigned_groups.all()
#         serializer = self.get_serializer(groups,many=True)
#         headers = self.get_success_headers(serializer.data)
#
#         return Response({'data': serializer.data})
#
#
#     # Removes the user from group
#     def destroy(self, request, *args, **kwargs):
#
#         print(self.kwargs)
#         IMRole.objects.get(id=self.kwargs['imrole_pk']).assigned_groups.remove(DjangoProject.objects.get(id=self.kwargs['pk']))
#
#         groups = IMRole.objects.get(id=self.kwargs['imrole_pk']).assigned_groups.all()
#         serializer = self.get_serializer(groups, many=True)
#         headers = self.get_success_headers(serializer.data)
#
#         return Response({'data': serializer.data})
#
#
# class IMRolePermissionViewSet(viewsets.ModelViewSet):
#     serializer_class = IMPermissionSerializer
#
#     def get_queryset(self):
#         role_id =self.kwargs['imrole_pk']
#         role = IMRole.objects.get(id=role_id)
#         queryset = role.permissions.all()
#         return queryset
#
#
#  # Creates the group membership record
#     def create(self, request, *args, **kwargs):
#         try:
#             imrole=IMRole.objects.get(id=self.kwargs['imrole_pk'])
#             perms = request.data['perm']
#             print(perms)
#
#             perm_list = str(perms).strip(' ').strip(',')
#             print(perm_list)
#             perm_list = perm_list.split(',')
#
#             for perm in perm_list:
#                 print(perm)
#                 perm_parts = perm.strip(' ').split(':')
#                 print(perm_parts)
#                 imrole.permissions.add(Permission.objects.get(name=perm_parts[2], content_type__model=perm_parts[1],content_type__app_label=perm_parts[0]))
#
#         except Exception as e:
#             logger.fatal(e);
#             logger.fatal('unable to add permission to role')
#
#         permissions = IMRole.objects.get(id=self.kwargs['imrole_pk']).permissions.all()
#         serializer = self.get_serializer(permissions, many=True)
#         headers = self.get_success_headers(serializer.data)
#
#         return Response({'data': serializer.data})
#
#
#     # Removes the user from group
#     def destroy(self, request, *args, **kwargs):
#
#         print(self.kwargs)
#         IMRole.objects.get(id=self.kwargs['imrole_pk']).permissions.remove(Permission.objects.get(id=self.kwargs['pk']))
#
#         permissions = IMRole.objects.get(id=self.kwargs['imrole_pk']).memberGroups.all()
#         serializer = self.get_serializer(permissions, many=True)
#         headers = self.get_success_headers(serializer.data)
#
#         return Response({'data': serializer.data})
#
#
