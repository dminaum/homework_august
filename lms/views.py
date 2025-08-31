from rest_framework import viewsets, generics, permissions
from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer
from .permissions import IsModer, IsOwner  # NEW

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all().prefetch_related('lessons')
    serializer_class = CourseSerializer

    def get_permissions(self):
        a = self.action
        if a == 'create':
            return [permissions.IsAuthenticated(), ~IsModer()]
        if a in ['update', 'partial_update']:
            return [permissions.IsAuthenticated(), (IsModer() | IsOwner())]
        if a == 'destroy':
            return [permissions.IsAuthenticated(), ~IsModer(), IsOwner()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        u = self.request.user
        if u.is_staff or u.groups.filter(name='moderators').exists():
            return Course.objects.all()
        return Course.objects.filter(owner=u)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonListCreateView(generics.ListCreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        u = self.request.user
        if u.is_staff or u.groups.filter(name='moderators').exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=u)

    def get_permissions(self):
        if self.request.method.lower() == 'post':
            return [permissions.IsAuthenticated(), ~IsModer()]
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
            return [permissions.IsAuthenticated(), (IsModer() | IsOwner())]
        if m == 'delete':
            return [permissions.IsAuthenticated(), ~IsModer(), IsOwner()]
        return [permissions.IsAuthenticated()]
