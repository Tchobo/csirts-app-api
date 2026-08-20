from rest_framework import serializers
from core.models import Csirt



class CsirtSerializer(serializers.ModelSerializer):
    """Compact CSIRT payload — used by list, create, and update endpoints."""

    name = serializers.CharField(
        help_text='Display name of the CSIRT (e.g. "bjCSIRT", "CERT-GH").'
    )
    country = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text='Country the CSIRT operates in. Optional, defaults to empty.',
    )
    website = serializers.CharField(
        help_text='Public website URL of the CSIRT.'
    )
    location = serializers.JSONField(
        help_text=(
            'JSON object with numeric latitude and longitude used to plot '
            'the CSIRT on the map. Keys are case-insensitive on input and '
            'coerced to lowercase floats on save. '
            'Example: {"latitude": 6.3703, "longitude": 2.3912}'
        )
    )
    contact = serializers.EmailField(
        help_text='Public contact email address of the CSIRT.'
    )
    image = serializers.ImageField(
        required=False,
        help_text='Optional logo or emblem image (multipart upload).',
    )

    class Meta:
        model=Csirt
        fields = [
            'id', 'name', 'location', 'contact', 'website', 'country', 'image'
            ]
        read_only_fields=['id']

    def validate_location(self, value):
        """Ensure location is a dict with numeric latitude/longitude.
        Accepts key casing variants (Latitude, LONGITUDE, ...) and numeric
        strings, but always stores lowercase keys with float values."""
        if not isinstance(value, dict):
            msg = "location must be a JSON object with latitude and longitude."
            raise serializers.ValidationError(msg)

        # Case-insensitive lookup so we forgive "Latitude", "LONGITUDE", etc.
        lower_map = {str(k).lower(): v for k, v in value.items()}
        try:
            lat = float(str(lower_map["latitude"]).replace(",", "."))
            lng = float(str(lower_map["longitude"]).replace(",", "."))
        except KeyError as exc:
            msg = f"location.{exc.args[0]} is required."
            raise serializers.ValidationError(msg) from exc
        except (TypeError, ValueError) as exc:
            msg = "location.latitude and location.longitude must be numeric."
            raise serializers.ValidationError(msg) from exc

        if not (-90 <= lat <= 90):
            msg = f"latitude must be between -90 and 90 (got {lat})."
            raise serializers.ValidationError(msg)
        if not (-180 <= lng <= 180):
            msg = f"longitude must be between -180 and 180 (got {lng})."
            raise serializers.ValidationError(msg)

        # Always persist canonical shape — lowercase keys, floats.
        return {"latitude": lat, "longitude": lng}

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
    """Full CSIRT payload — used by retrieve. Extends CsirtSerializer with
    the long-form description field for the detail view."""

    description = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text='Long-form description shown on the CSIRT detail card.',
    )

    class Meta(CsirtSerializer.Meta):
        # image is already in the parent fields — no need to duplicate.
        fields = CsirtSerializer.Meta.fields + ['description']


class CsirtImageSerializer(serializers.ModelSerializer):
    """Dedicated serializer for the upload-image action — accepts a single
    image file (multipart/form-data) and returns the CSIRT id + new image URL."""

    image = serializers.ImageField(
        required=True,
        help_text='Image file to attach to the CSIRT (PNG, JPEG, WEBP).',
    )

    class Meta:
        model = Csirt
        fields = ['id', 'image']
        read_only_fields = ['id']