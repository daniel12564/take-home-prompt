from rest_framework import serializers

from accounts.models import Account


class AccountSerializer(serializers.ModelSerializer):
    location_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Account
        fields = ['id', 'name', 'timezone', 'location_count']
