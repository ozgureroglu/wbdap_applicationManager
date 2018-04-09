from rest_framework import serializers

from applicationManager.models import Application,AppModel,Field


class FieldSerializer(serializers.ModelSerializer):
    # answer = serializers.StringRelatedField(many=True)


    class Meta:
        model = Field
        fields = ('id','name','field_type','definition','owner_model','type_parameter')



class AppModelSerializer(serializers.ModelSerializer):
    # answer = serializers.StringRelatedField(many=True)
    # owner_app_id = serializers.PrimaryKeyRelatedField(many=False,read_only=False, queryset=Application.objects.all())
    # Following is the reverse direction for read-only relation
    # owner_app = ApplicationSerializer(many=False, read_only=True)
    #TODO 3.7.8 ciktiginda hyperlinkedModelSerializer yine denenecek

    fields = FieldSerializer(many=True,read_only=True)
    class Meta:
        model = AppModel
        # fields = ('id','name','definition', 'owner_app','fields')
        fields = ('id','name','definition','owner_app', 'fields')


    def create(self, validated_data):

        print(validated_data)
        appmodel = AppModel.objects.create(**validated_data)
        # owner_app_id = self.request.data.get("owner_app_id")
        return appmodel

        # serializer.save(
        #     # Following is an extra argument to save
        #     application=Application.objects.get(id=owner_app_id),
        # )



class ApplicationSerializer(serializers.ModelSerializer):
    # answer = serializers.StringRelatedField(many=True)
    models = AppModelSerializer(many=True, read_only=True)
    class Meta:
        model=Application
        fields = ('app_name','verbose_name','url','namedUrl','active','models')


