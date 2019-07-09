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


from applicationManager.models import Application
from .serializers import (
    IMUserListSerializer,
    IMUserDetailSerializer,
    IMUserCreateSerializer,
    IMGroupListSerializer,
    IMGroupDetailSerializer,
    IMGroupCreateSerializer,
    IMRoleListSerializer,
    IMRoleDetailSerializer,
    IMRoleCreateSerializer,

    IMGroupSerializer,
    IMRoleSerializer,
    IMPermissionSerializer,
)

from projectCore.datatable_viewset import ModifiedViewSet
import logging

logger = logging.getLogger("api.views")


# Instead of using ViewSets (below tis section) we can create all CRUD views seperately and manualy :
# these views are accessed by Router Based Paths in api.urls.py instead of routers which provide the
# necessary paths automatically (which enables us to access views in a predefined path structrue)
# ----------- IMUSER ------------------------------

class IMUserCreateAPIView(CreateAPIView):
    queryset = IMUser.objects.all()
    serializer_class = IMUserCreateSerializer


class IMUserListAPIView(ListAPIView):
    queryset = IMUser.objects.all()
    serializer_class = IMUserListSerializer


class IMUserDetailAPIView(RetrieveAPIView):
    queryset = IMUser.objects.all()
    serializer_class = IMUserDetailSerializer
    # Asagidakileri degistirince urls icinde de abc pattern ile search yapilmasi gerekir
    # lookup_field = 'slug'
    # lookup_url_kwarg = 'abc'


class IMUserUpdateAPIView(RetrieveUpdateAPIView):
    queryset = IMUser.objects.all()
    serializer_class = IMUserDetailSerializer
    # Asagidakileri degistirince urls icinde de abc pattern ile search yapilmasi gerekir
    # lookup_field = 'slug'
    # lookup_url_kwarg = 'abc'


class IMUserDeleteAPIView(DestroyAPIView):
    queryset = IMUser.objects.all()
    serializer_class = IMUserDetailSerializer
    # Asagidakileri degistirince urls icinde de abc pattern ile search yapilmasi gerekir
    # lookup_field = 'slug'
    # lookup_url_kwarg = 'abc'


# ----------- IMGROUP ------------------------------

class IMGroupCreateAPIView(CreateAPIView):
    queryset = IMGroup.objects.all()
    serializer_class = IMGroupCreateSerializer


class IMGroupListAPIView(ListAPIView):
    queryset = IMGroup.objects.all()
    serializer_class = IMGroupListSerializer


class IMGroupDetailAPIView(RetrieveAPIView):
    queryset = IMGroup.objects.all()
    serializer_class = IMGroupDetailSerializer
    # Asagidakileri degistirince urls icinde de abc pattern ile search yapilmasi gerekir
    # lookup_field = 'slug'
    # lookup_url_kwarg = 'abc'


class IMGroupUpdateAPIView(RetrieveUpdateAPIView):
    queryset = IMGroup.objects.all()
    serializer_class = IMGroupDetailSerializer
    # Asagidakileri degistirince urls icinde de abc pattern ile search yapilmasi gerekir
    # lookup_field = 'slug'
    # lookup_url_kwarg = 'abc'


class IMGroupDeleteAPIView(DestroyAPIView):
    queryset = IMGroup.objects.all()
    serializer_class = IMGroupDetailSerializer
    # Asagidakileri degistirince urls icinde de abc pattern ile search yapilmasi gerekir
    # lookup_field = 'slug'
    # lookup_url_kwarg = 'abc'


# ----------- IMROLE ------------------------------

class IMRoleCreateAPIView(CreateAPIView):
    queryset = IMRole.objects.all()
    serializer_class = IMRoleCreateSerializer


class IMRoleListAPIView(ListAPIView):
    queryset = IMRole.objects.all()
    serializer_class = IMRoleListSerializer


class IMRoleDetailAPIView(RetrieveAPIView):
    queryset = IMRole.objects.all()
    serializer_class = IMRoleDetailSerializer
    # Asagidakileri degistirince urls icinde de abc pattern ile search yapilmasi gerekir
    # lookup_field = 'slug'
    # lookup_url_kwarg = 'abc'


class IMRoleUpdateAPIView(RetrieveUpdateAPIView):
    queryset = IMRole.objects.all()
    serializer_class = IMRoleDetailSerializer
    # Asagidakileri degistirince urls icinde de abc pattern ile search yapilmasi gerekir
    # lookup_field = 'slug'
    # lookup_url_kwarg = 'abc'


class IMRoleDeleteAPIView(DestroyAPIView):
    queryset = IMRole.objects.all()
    serializer_class = IMRoleDetailSerializer
    # Asagidakileri degistirince urls icinde de abc pattern ile search yapilmasi gerekir
    # lookup_field = 'slug'
    # lookup_url_kwarg = 'abc'


# -----------------------------------------

class IMUserViewSet(ModifiedViewSet):
    """
    API endpoint that allows users to view existing exams.
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """
    queryset = IMUser.objects.all()
    serializer_class = IMUserListSerializer
    filter_backends = (filters.OrderingFilter, filters.SearchFilter)
    search_fields = ('username','first_name','last_name','email',)
    ordering_fields = ('username','first_name','last_name','email','is_superuser','is_staff','is_active')


class IMGroupViewSet(ModifiedViewSet):
    """
    API endpoint that allows users to view existing exams. In fact this viewset
    allows us to do all CRUD operations on the object defined in the queryset
    parameter.
    """
    queryset = IMGroup.objects.all()
    serializer_class = IMGroupSerializer

    def update(self, request, *args, **kwargs):
        resp = super().update(request)
        return Response({'data': [resp.data]})

    def create(self, request, *args, **kwargs):
        resp = super().create(request)
        return Response({'data': [resp.data]})


class IMGroupMemberUserViewSet(viewsets.ModelViewSet):
    serializer_class = IMUserListSerializer

    def get_queryset(self):
        grp_id =self.kwargs['imgroup_pk']
        grp = IMGroup.objects.get(id=grp_id)
        queryset = grp.memberUsers.all()
        return queryset

    # Creates the group membership record
    def create(self, request, *args, **kwargs):
        try:
            imgroup=IMGroup.objects.get(id=self.kwargs['imgroup_pk'])
            usernames = request.data['username']

            username_list = str(usernames).strip(' ').strip(',')
            username_list = username_list.split(',')

            for username in username_list:
                print('adding %s' % username.strip())
                imgroup.memberUsers.add(IMUser.objects.get(username= username.strip(' ')))

        except Exception as e:
            logger.fatal(e);
            logger.fatal('unable to add user to group')

        members = IMGroup.objects.get(id=self.kwargs['imgroup_pk']).memberUsers.all()
        serializer = self.get_serializer(members,many=True)
        headers = self.get_success_headers(serializer.data)

        return Response({'data':serializer.data})


    # Removes the user from group
    def destroy(self, request, *args, **kwargs):
        print('delete')
        print(self.kwargs)
        IMGroup.objects.get(id=self.kwargs['imgroup_pk']).memberUsers.remove(IMUser.objects.get(id=self.kwargs['pk']))

        members = IMGroup.objects.get(id=self.kwargs['imgroup_pk']).memberUsers.all()
        serializer = self.get_serializer(members, many=True)
        headers = self.get_success_headers(serializer.data)

        return Response({'data': serializer.data})


class IMGroupMemberGroupViewSet(viewsets.ModelViewSet):
    serializer_class = IMGroupSerializer

    def get_queryset(self):
        grp_id =self.kwargs['imgroup_pk']
        grp = IMGroup.objects.get(id=grp_id)
        queryset = grp.memberGroups.all()
        return queryset


 # Creates the group membership record
    def create(self, request, *args, **kwargs):
        try:
            imgroup=IMGroup.objects.get(id=self.kwargs['imgroup_pk'])
            subgrp_names = request.data['name']

            subgrp_name_list = str(subgrp_names).strip(' ').strip(',')
            subgrp_name_list = subgrp_name_list.split(',')

            for subgrp_name in subgrp_name_list:
                print('adding %s' % subgrp_name.strip())
                imgroup.memberGroups.add(IMGroup.objects.get(name=subgrp_name.strip(' ')))

        except Exception as e:
            logger.fatal(e);
            logger.fatal('unable to add group to group')

        members = IMGroup.objects.get(id=self.kwargs['imgroup_pk']).memberGroups.all()
        serializer = self.get_serializer(members,many=True)
        headers = self.get_success_headers(serializer.data)

        return Response({'data': serializer.data})


    # Removes the user from group
    def destroy(self, request, *args, **kwargs):
        print('delete')
        print(self.kwargs)
        IMGroup.objects.get(id=self.kwargs['imgroup_pk']).memberGroups.remove(IMGroup.objects.get(id=self.kwargs['pk']))

        members = IMGroup.objects.get(id=self.kwargs['imgroup_pk']).memberGroups.all()
        serializer = self.get_serializer(members, many=True)
        headers = self.get_success_headers(serializer.data)

        return Response({'data': serializer.data})


class IMRoleViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to view existing exams
    """
    queryset = IMRole.objects.all()
    serializer_class = IMRoleSerializer

    filter_backends = (filters.OrderingFilter, filters.SearchFilter)
    search_fields = ('name',)
    ordering_fields = ('name',)

    def update(self, request, *args, **kwargs):
        resp = super().update(request)
        return Response({'data': [resp.data]})


    def create(self, request, *args, **kwargs):
        resp = super().create(request)
        return Response({'data': [resp.data]})


class IMRoleAssignedUserViewSet(viewsets.ModelViewSet):
    serializer_class = IMUserListSerializer

    def get_queryset(self):
        role_id =self.kwargs['imrole_pk']
        role = IMRole.objects.get(id=role_id)
        queryset = role.assigned_users.all()
        return queryset

    # Creates the role membership record
    def create(self, request, *args, **kwargs):
        try:
            imrole=IMRole.objects.get(id=self.kwargs['imrole_pk'])
            usernames = request.data['username']

            username_list = str(usernames).strip(' ').strip(',')
            username_list = username_list.split(',')

            for username in username_list:
                print('adding %s' % username.strip())
                imrole.assigned_users.add(IMUser.objects.get(username= username.strip(' ')))

        except Exception as e:
            logger.fatal(e);
            logger.fatal('unable to add user to group')

        members = IMRole.objects.get(id=self.kwargs['imrole_pk']).assigned_users.all()
        serializer = self.get_serializer(members, many=True)
        headers = self.get_success_headers(serializer.data)

        return Response({'data':serializer.data})


    # Removes the user from group
    def destroy(self, request, *args, **kwargs):

        print(self.kwargs)
        IMRole.objects.get(id=self.kwargs['imrole_pk']).assigned_users.remove(IMUser.objects.get(id=self.kwargs['pk']))

        users = IMRole.objects.get(id=self.kwargs['imrole_pk']).assigned_users.all()
        serializer = self.get_serializer(users, many=True)
        headers = self.get_success_headers(serializer.data)

        return Response({'data': serializer.data})


class IMRoleAssignedGroupViewSet(viewsets.ModelViewSet):
    serializer_class = IMGroupSerializer

    def get_queryset(self):
        role_id =self.kwargs['imrole_pk']
        role = IMRole.objects.get(id=role_id)
        queryset = role.assigned_groups.all()
        return queryset


 # Creates the group membership record
    def create(self, request, *args, **kwargs):
        try:
            imrole=IMRole.objects.get(id=self.kwargs['imrole_pk'])
            subgrp_names = request.data['name']

            subgrp_name_list = str(subgrp_names).strip(' ').strip(',')
            subgrp_name_list = subgrp_name_list.split(',')

            for subgrp_name in subgrp_name_list:
                print('adding %s' % subgrp_name.strip())
                imrole.assigned_groups.add(IMGroup.objects.get(name=subgrp_name.strip(' ')))

        except Exception as e:
            logger.fatal(e);
            logger.fatal('unable to add group to group')

        groups = IMRole.objects.get(id=self.kwargs['imrole_pk']).assigned_groups.all()
        serializer = self.get_serializer(groups,many=True)
        headers = self.get_success_headers(serializer.data)

        return Response({'data': serializer.data})


    # Removes the user from group
    def destroy(self, request, *args, **kwargs):

        print(self.kwargs)
        IMRole.objects.get(id=self.kwargs['imrole_pk']).assigned_groups.remove(IMGroup.objects.get(id=self.kwargs['pk']))

        groups = IMRole.objects.get(id=self.kwargs['imrole_pk']).assigned_groups.all()
        serializer = self.get_serializer(groups, many=True)
        headers = self.get_success_headers(serializer.data)

        return Response({'data': serializer.data})


class IMRolePermissionViewSet(viewsets.ModelViewSet):
    serializer_class = IMPermissionSerializer

    def get_queryset(self):
        role_id =self.kwargs['imrole_pk']
        role = IMRole.objects.get(id=role_id)
        queryset = role.permissions.all()
        return queryset


 # Creates the group membership record
    def create(self, request, *args, **kwargs):
        try:
            imrole=IMRole.objects.get(id=self.kwargs['imrole_pk'])
            perms = request.data['perm']
            print(perms)

            perm_list = str(perms).strip(' ').strip(',')
            print(perm_list)
            perm_list = perm_list.split(',')

            for perm in perm_list:
                print(perm)
                perm_parts = perm.strip(' ').split(':')
                print(perm_parts)
                imrole.permissions.add(Permission.objects.get(name=perm_parts[2], content_type__model=perm_parts[1],content_type__app_label=perm_parts[0]))

        except Exception as e:
            logger.fatal(e);
            logger.fatal('unable to add permission to role')

        permissions = IMRole.objects.get(id=self.kwargs['imrole_pk']).permissions.all()
        serializer = self.get_serializer(permissions, many=True)
        headers = self.get_success_headers(serializer.data)

        return Response({'data': serializer.data})


    # Removes the user from group
    def destroy(self, request, *args, **kwargs):

        print(self.kwargs)
        IMRole.objects.get(id=self.kwargs['imrole_pk']).permissions.remove(Permission.objects.get(id=self.kwargs['pk']))

        permissions = IMRole.objects.get(id=self.kwargs['imrole_pk']).memberGroups.all()
        serializer = self.get_serializer(permissions, many=True)
        headers = self.get_success_headers(serializer.data)

        return Response({'data': serializer.data})


