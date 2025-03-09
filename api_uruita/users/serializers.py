from rest_framework import serializers
from django.contrib.auth import get_user_model

from users.services import send_verification_email

User = get_user_model()

class UserRegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True, min_length=6)
    password = serializers.CharField(write_only=True, min_length=6)
    
    class Meta:
        model = User
        fields = ['cpf','username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            cpf=validated_data['cpf'],
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
        )
        user.generate_verification_code()

        send_verification_email(user)

        return user

class VerifyEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=4)

class LoginSerializer(serializers.Serializer):
    cpf = serializers.CharField() 
    password = serializers.CharField(write_only=True)
