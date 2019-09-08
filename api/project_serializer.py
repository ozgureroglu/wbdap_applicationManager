from rest_framework.serializers import HyperlinkedModelSerializer, HyperlinkedIdentityField, ModelSerializer
from applicationManager.models import  DjangoProject
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType


# --------- CRUD Serializers -----------------------------
# https://www.youtube.com/watch?v=dfIB-LthIpE&list=PLEsfXFp6DpzTOcOVdZF-th7BS_GYGguAS&index=9



class DjangoProjectCreateSerializer(ModelSerializer):

    class Meta:
        model = DjangoProject
        fields = ('name', 'port', 'description')
        # Following kwarg avoids the password to be returned
        # extra_kwargs = {'password': {'write_only': True}}

    def create(self,validated_data):
        """
        This method overrides the ModelSerializers create method, so that model creation behaves differently than
        the default one. If we want to change the create behaviour at APIView level this method will be defined as
        perform_create() which overrides the perform_create() method of CreateModelMixin and this method simply calls
        serializer.save(). So we can pass parameters to save method to override data fields
        such as serializer.save(user=self.request.user)

        to serializer.save
        :param validated_data:
        :return:
        """
        dproject = DjangoProject.objects.create(
            name=validated_data['name'],
            port=validated_data['port'],
            description=validated_data['description'],

        )
        return dproject


class DjangoProjectListSerializer(HyperlinkedModelSerializer):
    url = HyperlinkedIdentityField(view_name="applicationManager-api:djangoproject-detail")

    class Meta:
        model = DjangoProject
        fields = ('id', 'name', 'url','port', 'description')


class DjangoProjectDetailSerializer(ModelSerializer):

    class Meta:
        model = DjangoProject
        fields = ('id', 'name', 'port', 'description', 'status')


# ---------------------------------------------------------------
