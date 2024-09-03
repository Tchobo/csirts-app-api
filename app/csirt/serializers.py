from rest_framework import serializers
from core.models import Csirt



class CsirtSerializer(serializers.ModelSerializer):
    location = serializers.JSONField(
        help_text="A JSON object containing two key value data. For example: {\"longitude\": \"123123\", \"latitude\": \"0.123456\"}"
    )
    contact = serializers.EmailField(
        help_text="An Email adress of the csirt company."
    )
    
    class Meta:
        model=Csirt
        fields = [
            'id', 'name', 'location', 'contact', 'website',
            ]
        read_only_fields=['id']

    def create(self, validated_data):
        """Create a csirt."""
        csirt = Csirt.objects.create(**validated_data)
        return csirt
    
    def update(self, instance, validated_data):
        """Update csirt."""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)   

        instance.save()
        return instance
    

class CsirtDetailSerializer(CsirtSerializer):
    """Serializer for csirt detail view."""

    class Meta(CsirtSerializer.Meta):
        fields = CsirtSerializer.Meta.fields + ['description', 'image', ]


class CsirtImageSerializer(serializers.ModelSerializer):
    """Serializer for uploading images to Csirts."""

    class Meta:
        model = Csirt
        fields= ['id', 'image']
        read_only_fields = ['id']
        extra_kwargs = {'image': {'required':'True'}}