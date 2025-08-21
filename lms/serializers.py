from rest_framework import serializers
from .models import Course, Lesson


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = '__all__'


class CourseSerializer(serializers.ModelSerializer):
    lessons_count = serializers.SerializerMethodField()  # ← новое поле
    lessons = LessonSerializer(many=True, read_only=True)  # (если нужно ещё и список уроков)

    class Meta:
        model = Course
        fields = '__all__'

    def get_lessons_count(obj):
        return obj.lessons.count()
