# serializers.py
from rest_framework import serializers
from .models import Package, Days, BookedPackage,PackageCategory
from resorts.serializers import ResortSerializer
from resorts.models import  Resort  
from users.models import User

class UserPackageSerializer(serializers.ModelSerializer):
    first_day_image = serializers.SerializerMethodField()

    class Meta:
        model = Package
        fields = ['id','start','end','is_holiday','days', 'name', 'base_price', 'adult_price', 'child_price','category', 'first_day_image','valid']

    def get_first_day_image(self, obj):
        first_day = obj.days_package.first() 
        if first_day and first_day.place_photo:
            return first_day.place_photo  
        return None  


class DaysSerializer(serializers.ModelSerializer):
    class Meta:
        model = Days
        fields = ['package', 'day', 'place_name', 'activity', 'place_photo', 'resort']


class PackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Package
        fields = '__all__'

    def validate(self, data):
        # Check for uniqueness of the 'name' field during creation
        if self.instance is None:  # This is a create operation
            if Package.objects.filter(name__iexact=data.get('name')).exists():
                raise serializers.ValidationError({
                    'name': '! category with this name already exists.'
                })
        else:  # This is an update operation
            if 'name' in data and Package.objects.filter(name__iexact   =data.get('name')).exclude(pk=self.instance.pk).exists():
                raise serializers.ValidationError({
                    'name': '! category with this name already exists.'
                })
        return data




class BookedPackageSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.last_name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_phone = serializers.CharField(source='user.phone_number', read_only=True)
    package_name = serializers.CharField(source='package.name', read_only=True)
    image = serializers.SerializerMethodField()

    class Meta:
        model = BookedPackage
        fields = [
            'id', 'user', 'package', 'user_name', 'user_email', 'user_phone', 
            'package_name', 'adult_count', 'child_count', 'paid_amount', 
            'total_amount', 'date', 'conformed', 'image'
        ]

    def get_image(self, obj):
        first_day = obj.package.days_package.first() 
        return first_day.place_photo if first_day else None



class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PackageCategory
        fields = ['id', 'name', 'description']

    def validate(self, data):
        # Check for uniqueness of the 'name' field during creation
        if self.instance is None:  # This is a create operation
            if PackageCategory.objects.filter(name__iexact=data.get('name')).exists():
                raise serializers.ValidationError({
                    'name': '! category with this name already exists.'
                })
        else:  # This is an update operation
            if 'name' in data and PackageCategory.objects.filter(name__iexact   =data.get('name')).exclude(pk=self.instance.pk).exists():
                raise serializers.ValidationError({
                    'name': '! category with this name already exists.'
                })
        return data
    

