from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail



User = get_user_model()

class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ['email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, validators=[validate_password])

class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()
    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")
        self.context['user'] = user
        return value

    def save(self):
        user = self.context['user']
        token = PasswordResetTokenGenerator().make_token(user)
        reset_url = f"http://localhost:8000/reset-password/{user.pk}/{token}/"  
        send_mail(
            "Password Reset Request",
            f"Click the link to reset your password: {reset_url}",
            "business993355b@gmail.com",
            [user.email],
        )

class PasswordResetConfirmSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True)
    token = serializers.CharField()
    user_id = serializers.IntegerField()

    def validate(self, data):
        try:
            user = User.objects.get(pk=data['user_id'])
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid user.")

        if not PasswordResetTokenGenerator().check_token(user, data['token']):
            raise serializers.ValidationError("Invalid token.")
        self.context['user'] = user
        return data

    def save(self):
        user = self.context['user']
        user.set_password(self.validated_data['new_password'])
        user.save()



