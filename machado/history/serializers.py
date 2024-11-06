from rest_framework import serializers
from machado.history.models import History
from machado.account.serializers import UserSerializer

class HistorySerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = History
        fields = ['id', 'user', 'description', 'method', 'created_at']