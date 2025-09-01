from rest_framework import viewsets, generics, permissions, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Course, Lesson, Subscription
from .pagination import MyPagination
from .serializers import CourseSerializer, LessonSerializer
from .permissions import IsOwner, ModerOrOwner, NotModer


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all().prefetch_related('lessons')
    serializer_class = CourseSerializer
    pagination_class = MyPagination

    def get_permissions(self):
        a = self.action
        if a == 'create':
            return [permissions.IsAuthenticated(), NotModer()]
        if a in ['update', 'partial_update']:
            return [permissions.IsAuthenticated(), ModerOrOwner()]
        if a == 'destroy':
            return [permissions.IsAuthenticated(), NotModer(), IsOwner()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        u = self.request.user
        if u.is_staff or u.groups.filter(name='moderators').exists():
            return Course.objects.all()
        return Course.objects.filter(owner=u)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class SubscriptionToggleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        course_id = request.data.get("course_id")
        if not course_id:
            return Response({"detail": "course_id is required"}, status=400)

        course = get_object_or_404(Course, pk=course_id)

        qs = Subscription.objects.filter(user=user, course=course)
        if qs.exists():
            qs.delete()
            return Response(
                {"message": "подписка удалена", "course_id": course.id, "is_subscribed": False},
                status=status.HTTP_200_OK,
            )
        else:
            Subscription.objects.create(user=user, course=course)
            return Response(
                {"message": "подписка добавлена", "course_id": course.id, "is_subscribed": True},
                status=status.HTTP_201_CREATED,
            )


class LessonListCreateView(generics.ListCreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = MyPagination

    def get_queryset(self):
        u = self.request.user
        if u.is_staff or u.groups.filter(name='moderators').exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=u)

    def get_permissions(self):
        if self.request.method.lower() == 'post':
            return [permissions.IsAuthenticated(), NotModer()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        m = self.request.method.lower()
        if m in ['put', 'patch']:
            return [permissions.IsAuthenticated(), ModerOrOwner()]
        if m == 'delete':
            return [permissions.IsAuthenticated(), NotModer(), IsOwner()]
        return [permissions.IsAuthenticated()]
