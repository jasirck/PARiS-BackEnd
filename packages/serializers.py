# serializers.py
from rest_framework import serializers
from .models import Package, Days, BookedPackage
from .models import Package, Resort  
from users.models import User

class ResortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resort
        fields = '__all__'


class PackageSerializer(serializers.ModelSerializer):
    resort = serializers.PrimaryKeyRelatedField(queryset=Resort.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Package
        fields = '__all__'

class DaysSerializer(serializers.ModelSerializer):
    package = serializers.PrimaryKeyRelatedField(queryset=Package.objects.all())
    resort = ResortSerializer(required=False)

    class Meta:
        model = Days
        fields = '__all__'

class BookedPackageSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    package = PackageSerializer()
    resort = ResortSerializer(required=False)

    class Meta:
        model = BookedPackage
        fields = '__all__'
