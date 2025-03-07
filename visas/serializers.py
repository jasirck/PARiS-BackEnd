from rest_framework import serializers
from .models import VisaCategory, Visa, VisaDays, VisaBooked
from users.models import User


class VisaCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = VisaCategory
        fields = "__all__"


class VisaDaysSerializer(serializers.ModelSerializer):
    class Meta:
        model = VisaDays
        fields = ["id", "visa", "days", "price"]


class VisaSerializer(serializers.ModelSerializer):

    class Meta:
        model = Visa
        fields = ["id", "name", "category", "place_photo", "note"]


class GetVisaSerializer(serializers.ModelSerializer):
    visa_days = VisaDaysSerializer(many=True)  # Include related VisaDays
    category = VisaCategorySerializer()

    class Meta:
        model = Visa
        fields = ["id", "name", "category", "place_photo", "note", "visa_days"]


class VisaBookedSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    booked_visa = serializers.PrimaryKeyRelatedField(queryset=Visa.objects.all())
    days = serializers.PrimaryKeyRelatedField(queryset=VisaDays.objects.all())

    passport = serializers.CharField()
    photo = serializers.CharField()

    # Adding related fields to display additional data (e.g., visa place photo)
    booked_visa_name = serializers.CharField(source="booked_visa.name", read_only=True)
    booked_visa_place_photo = serializers.CharField(
        source="booked_visa.place_photo", read_only=True
    )
    user_name = serializers.CharField(source="user.last_name", read_only=True)
    day = serializers.CharField(source="days.days", read_only=True)
    price = serializers.DecimalField(
        source="days.price", max_digits=10, decimal_places=2
    )
    number = serializers.CharField(source="user.phone", read_only=True)
    email = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = VisaBooked
        fields = [
            "id",
            "user",
            "days",
            "passport",
            "photo",
            "conformed",
            "booked_visa",
            "booked_visa_name",
            "booked_visa_place_photo",
            "created_at",
            "user_name",
            "day",
            "price",
            "number",
            "email",
        ]


class AdminBookedVisaSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all()
    )  # Instead of user_id
    booked_visa = serializers.PrimaryKeyRelatedField(queryset=Visa.objects.all())
    days = serializers.PrimaryKeyRelatedField(
        queryset=VisaDays.objects.all()
    )  # Use days instead of days_id
    passport = serializers.CharField()  # Passport photo data
    photo = serializers.CharField()  # Personal photo data
    status = serializers.CharField(default="Requested")  # Provide a default status

    class Meta:
        model = VisaBooked
        fields = ["id", "user", "booked_visa", "days", "passport", "photo", "status"]

    def create(self, validated_data):
        # Using the validated data directly to create the booking
        user = validated_data["user"]
        days = validated_data["days"]
        booked_visa = validated_data["booked_visa"]
        passport = validated_data["passport"]
        photo = validated_data["photo"]

        booked_visa_instance = VisaBooked.objects.create(
            user=user,
            days=days,
            booked_visa=booked_visa,
            passport=passport,
            photo=photo,
        )
        return booked_visa_instance
