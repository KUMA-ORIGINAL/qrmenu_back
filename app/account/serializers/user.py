from django.contrib.auth import get_user_model
from rest_framework import serializers

from .achievement_and_rarity import AchievementSerializer

User = get_user_model()

class MeSerializer(serializers.ModelSerializer):
    achievements = AchievementSerializer(many=True)
    group = serializers.StringRelatedField()

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                  'photo', 'role', 'group', 'achievements_count', 'points', 'rating',
                  'achievements',)

class MeUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'photo')


class UserListSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'photo', 'points', 'rating')
