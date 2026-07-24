from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, FarmerProfile, BuyerProfile


class FarmerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = FarmerProfile
        fields = ['state', 'lga', 'preferred_language', 'farm_size_hectares']


class BuyerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = BuyerProfile
        fields = ['business_name', 'location', 'verified_status']


class UserSerializer(serializers.ModelSerializer):
    farmer_profile = FarmerProfileSerializer(read_only=True)
    buyer_profile = BuyerProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'role', 'phone', 'wallet_balance', 'farmer_profile', 'buyer_profile',
        ]
        read_only_fields = ['id', 'wallet_balance']


class RegisterSerializer(serializers.ModelSerializer):
    """Handles registration for any role."""
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)

    # Farmer-specific optional fields
    state = serializers.CharField(required=False, allow_blank=True)
    lga = serializers.CharField(required=False, allow_blank=True)
    preferred_language = serializers.ChoiceField(
        choices=FarmerProfile.Language.choices,
        required=False,
        default='en',
    )

    # Buyer-specific optional fields
    business_name = serializers.CharField(required=False, allow_blank=True)
    location = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password2',
            'first_name', 'last_name', 'role', 'phone',
            'state', 'lga', 'preferred_language',
            'business_name', 'location',
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs.pop('password2'):
            raise serializers.ValidationError({'password': 'Passwords do not match.'})
        return attrs

    def create(self, validated_data):
        # Extract farmer-profile fields
        state = validated_data.pop('state', '')
        lga = validated_data.pop('lga', '')
        preferred_language = validated_data.pop('preferred_language', 'en')

        # Extract buyer-profile fields
        business_name = validated_data.pop('business_name', '')
        location = validated_data.pop('location', '')

        user = User.objects.create_user(**validated_data)

        if user.role == User.Role.FARMER:
            FarmerProfile.objects.create(
                user=user,
                state=state,
                lga=lga,
                preferred_language=preferred_language,
            )
        elif user.role == User.Role.BUYER:
            from .models import BuyerProfile
            BuyerProfile.objects.create(
                user=user,
                business_name=business_name,
                location=location,
            )

        return user
