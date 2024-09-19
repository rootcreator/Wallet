from rest_framework import serializers
from .models import Wallet, Transaction, UserProfile
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['id', 'user', 'balance']


class DepositSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    currency = serializers.CharField(max_length=3, default='USD')


class TransferSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    currency = serializers.CharField(max_length=3, default='USD')
    destination_tag = serializers.CharField(max_length=56)


class WithdrawSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    currency = serializers.CharField(max_length=3, default='USD')
    destination_public_key = serializers.CharField(max_length=56)


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'wallet', 'amount', 'transaction_type', 'timestamp']

    @staticmethod
    def validate_amount(value):
        if value <= 0:
            raise serializers.ValidationError('Amount must be positive.')
        return value


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['user', 'wallet', 'country', 'dob', 'kyc_status', 'kyc_document']

    def update(self, instance, validated_data):
        instance.country = validated_data.get('country', instance.country)
        instance.bio = validated_data.get('bio', instance.bio)
        instance.kyc_document = validated_data.get('kyc_document', instance.kyc_document)
        instance.save()
        return instance
