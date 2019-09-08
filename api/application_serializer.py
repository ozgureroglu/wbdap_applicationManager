from rest_framework.serializers import HyperlinkedModelSerializer, HyperlinkedIdentityField, ModelSerializer
from applicationManager.models import Application
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType


# --------- CRUD Serializers -----------------------------
# https://www.youtube.com/watch?v=dfIB-LthIpE&list=PLEsfXFp6DpzTOcOVdZF-th7BS_GYGguAS&index=9



class ApplicationCreateSerializer(ModelSerializer):

    class Meta:
        model = Application
        fields = ('app_name', 'verbose_name', 'url','description')
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
        app = Application.objects.create(
            name=validated_data['name'],
            description=validated_data['description'],
            # first_name=validated_data['first_name'],
            # last_name=validated_data['last_name'],
            # email=validated_data['email'],
            # password=make_password(validated_data['password'])
        )
        return app


class ApplicationListSerializer(HyperlinkedModelSerializer):
    url = HyperlinkedIdentityField(view_name="identityManager-api:imgroup-detail")

    class Meta:
        model = Application
        fields = ('id', 'app_name', 'verbose_name', 'url', 'description')


class ApplicationDetailSerializer(ModelSerializer):

    class Meta:
        model = Application
        fields = ('id', 'app_name', 'description', 'url')


# ---------------------------------------------------------------

