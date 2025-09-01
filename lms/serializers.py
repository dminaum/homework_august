from rest_framework import serializers
from .models import Course, Lesson, Subscription
from .validators import validate_youtube_url


class LessonSerializer(serializers.ModelSerializer):
    video_url = serializers.URLField(
        required=False,
        allow_null=True,
        allow_blank=True,
        validators=[validate_youtube_url]
    )
    class Meta:
        model = Lesson
        fields = '__all__'
        read_only_fields = ('owner',)


class CourseSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    lessons_count = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = '__all__'
        read_only_fields = ('owner',)

    def get_lessons_count(self, obj):
        return obj.lessons.count()

    def get_is_subscribed(self, obj):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return False
        return Subscription.objects.filter(user=user, course=obj).exists()
