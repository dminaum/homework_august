from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import override_settings
from rest_framework.test import APITestCase
from rest_framework import status
from django.core.exceptions import FieldDoesNotExist
from django.db import models as djm

from lms.models import Course, Lesson, Subscription


def unpack_list(resp):
    """Вернёт список объектов независимо от пагинации."""
    if isinstance(resp.data, dict) and "results" in resp.data:
        return resp.data["results"]
    return resp.data


def pick_title_field(model, candidates=("name", "title")) -> str:
    """Ищет подходящее строковое поле (name/title) в модели."""
    for c in candidates:
        try:
            model._meta.get_field(c)
            return c
        except FieldDoesNotExist:
            continue
    for f in model._meta.get_fields():
        if getattr(f, "concrete", False) and not getattr(f, "many_to_many", False) and f.name != "id":
            if isinstance(f, (djm.CharField, djm.TextField)):
                return f.name
    raise AssertionError(f"Не нашёл строкового поля у {model.__name__}")


@override_settings(DEFAULT_PERMISSION_CLASSES=[])
class BaseAPITestCase(APITestCase):
    """
    Базовая инициализация данных:
    - группа moderators
    - пользователи: owner, other, moder
    - курс (owner)
    - два урока: owner-lesson и other-lesson
    """

    def setUp(self):
        User = get_user_model()
        self.group_moderators, _ = Group.objects.get_or_create(name="moderators")

        self.owner = User.objects.create(email="owner@test.com")
        self.other = User.objects.create(email="other@test.com")
        self.moder = User.objects.create(email="moder@test.com")
        self.moder.groups.add(self.group_moderators)

        self.lesson_title_field = pick_title_field(Lesson, ("name", "title"))

        self.lessons_url = "/api/lessons/"
        self.lesson_detail = lambda pk: f"/api/lessons/{pk}/"
        self.courses_url = "/api/courses/"
        self.course_detail = lambda pk: f"/api/courses/{pk}/"
        self.subs_toggle_url = "/api/subscriptions/toggle/"

        self.course = Course.objects.create(name="Course 1", owner=self.owner)
        self.lesson_owner = Lesson.objects.create(name="L1", course=self.course, owner=self.owner)
        self.lesson_other = Lesson.objects.create(name="L2", course=self.course, owner=self.other)

    def as_owner(self):
        self.client.force_authenticate(user=self.owner)

    def as_other(self):
        self.client.force_authenticate(user=self.other)

    def as_moder(self):
        self.client.force_authenticate(user=self.moder)


class LessonCRUDTests(BaseAPITestCase):
    def test_lessons_list_as_moderator_sees_all(self):
        self.as_moder()
        r = self.client.get(self.lessons_url)
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        items = unpack_list(r)
        self.assertEqual(len(items), 2, r.data)

    def test_lessons_list_as_user_sees_only_own(self):
        self.as_owner()
        r = self.client.get(self.lessons_url)
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        items = unpack_list(r)
        self.assertEqual(len(items), 1, r.data)
        ids = {obj.get("id") for obj in items}
        self.assertIn(self.lesson_owner.id, ids)
        self.assertNotIn(self.lesson_other.id, ids)

    def test_lessons_create_by_user_allowed(self):
        self.as_owner()
        payload = {
            self.lesson_title_field: "New lesson",
            "course": self.course.id,
            "description": "текст"
        }
        r = self.client.post(self.lessons_url, payload, format="json")
        self.assertEqual(r.status_code, status.HTTP_201_CREATED, r.data)
        self.assertTrue(Lesson.objects.filter(**{self.lesson_title_field: "New lesson"}, owner=self.owner).exists())

    def test_lessons_create_by_moderator_forbidden(self):
        self.as_moder()
        payload = {self.lesson_title_field: "Mod lesson", "course": self.course.id}
        r = self.client.post(self.lessons_url, payload, format="json")
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN, r.data)

    def test_lessons_update_by_owner_allowed(self):
        self.as_owner()
        r = self.client.patch(self.lesson_owner and self.lesson_detail(self.lesson_owner.id),
                              {"name": "L1-upd"}, format="json")
        self.assertEqual(r.status_code, status.HTTP_200_OK, r.data)
        self.lesson_owner.refresh_from_db()
        self.assertEqual(self.lesson_owner.name, "L1-upd")

    def test_lessons_update_by_moderator_allowed_for_any(self):
        self.as_moder()
        r = self.client.patch(self.lesson_detail(self.lesson_other.id),
                              {"name": "L2-upd-by-moder"}, format="json")
        self.assertEqual(r.status_code, status.HTTP_200_OK, r.data)
        self.lesson_other.refresh_from_db()
        self.assertEqual(self.lesson_other.name, "L2-upd-by-moder")

    def test_lessons_update_by_non_owner_forbidden(self):
        self.as_other()
        r = self.client.patch(self.lesson_detail(self.lesson_owner.id),
                              {"name": "try-upd"}, format="json")
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN, r.data)

    def test_lessons_delete_by_owner_allowed(self):
        self.as_owner()
        r = self.client.delete(self.lesson_detail(self.lesson_owner.id))
        self.assertEqual(r.status_code, status.HTTP_204_NO_CONTENT, r.data)
        self.assertFalse(Lesson.objects.filter(id=self.lesson_owner.id).exists())

    def test_lessons_delete_by_moderator_forbidden(self):
        self.as_moder()
        r = self.client.delete(self.lesson_detail(self.lesson_other.id))
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN, r.data)

    def test_lessons_delete_by_non_owner_forbidden(self):
        self.as_other()
        r = self.client.delete(self.lesson_detail(self.lesson_owner.id))
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN, r.data)


class SubscriptionTests(BaseAPITestCase):
    def test_toggle_subscription_add_then_remove(self):
        self.as_owner()

        r1 = self.client.post(self.subs_toggle_url, {"course_id": self.course.id}, format="json")
        self.assertEqual(r1.status_code, status.HTTP_201_CREATED, r1.data)
        self.assertTrue(
            Subscription.objects.filter(user=self.owner, course=self.course).exists()
        )

        r_course = self.client.get(self.course_detail(self.course.id))
        self.assertEqual(r_course.status_code, status.HTTP_200_OK, r_course.data)
        self.assertTrue(r_course.data.get("is_subscribed") is True)

        r2 = self.client.post(self.subs_toggle_url, {"course_id": self.course.id}, format="json")
        self.assertEqual(r2.status_code, status.HTTP_200_OK, r2.data)
        self.assertFalse(
            Subscription.objects.filter(user=self.owner, course=self.course).exists()
        )

        r_course2 = self.client.get(self.course_detail(self.course.id))
        self.assertEqual(r_course2.status_code, status.HTTP_200_OK, r_course2.data)
        self.assertTrue(r_course2.data.get("is_subscribed") is False)
