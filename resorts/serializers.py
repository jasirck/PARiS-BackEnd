from rest_framework import serializers
from .models import Resort, ResortImages,ResortCategory

class ResortImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResortImages
        fields = ['id', 'image']




class ResortSerializer(serializers.ModelSerializer):    
    images = ResortImageSerializer(many=True, read_only=True)
    category = serializers.PrimaryKeyRelatedField(queryset=ResortCategory.objects.all())

    class Meta:
        model = Resort
        fields = [
            'id', 'name', 'location', 'pool', 'package_inclusions',
            'base_price', 'adult_price', 'child_price', 'policy',
            'valid', 'category', 'images',
        ]



class UserResortSerializer(serializers.ModelSerializer):
    images = ResortImageSerializer(many=True, read_only=True)

    class Meta:
        model = Resort
        fields = ['id', 'name', 'pool', 'base_price', 'adult_price', 'child_price', 'images','category_id']

    def to_representation(self, instance):
        # Limit images to only one in the response
        representation = super().to_representation(instance)
        representation['images'] = representation['images'][:1]  # Only include the first image
        return representation




class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ResortCategory
        fields = ['id', 'name', 'description']

    def validate(self, data):
        # Check for uniqueness of the 'name' field during creation
        if self.instance is None:  # This is a create operation
            if ResortCategory.objects.filter(name__iexact=data.get('name')).exists():
                raise serializers.ValidationError({
                    'name': '! category with this name already exists.'
                })
        else:  # This is an update operation
            if 'name' in data and ResortCategory.objects.filter(name__iexact   =data.get('name')).exclude(pk=self.instance.pk).exists():
                raise serializers.ValidationError({
                    'name': '! category with this name already exists.'
                })
        return data