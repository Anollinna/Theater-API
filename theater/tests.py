import tempfile
import os

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from theater.models import Play, Actor, Genre
from theater.serializers import PlayListSerializer
from django.contrib.auth import get_user_model
from PIL import Image


PLAY_URL = reverse("theater:play-list")


def detail_url(play_id):
    return reverse("theater:play-detail", args=[play_id])


def upload_image_url(play_id):
    return reverse("theater:play-upload-image", args=[play_id])


def sample_genre(name="Comedy"):
    return Genre.objects.create(name=name)

def sample_actor(name="John Doe"):
    return Actor.objects.create(first_name=name, last_name=name)


class PublicPlayApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_list_plays(self):
        genre = Genre.objects.create(name="Comedy")
        actor = Actor.objects.create(first_name="Tom", last_name="Hanks")
        play = Play.objects.create(title="Funny Show", description="Great comedy")
        play.genres.add(genre)
        play.actors.add(actor)

        res = self.client.get(PLAY_URL)
        plays = Play.objects.all()
        serializer = PlayListSerializer(plays, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_filter_plays_by_title(self):
        Play.objects.create(title="Dramatic Play", description="Drama")
        Play.objects.create(title="Musical Show", description="Music")

        res = self.client.get(PLAY_URL, {"title": "drama"})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 1)
        self.assertIn("Dramatic Play", res.data["results"][0]["title"])

    def test_filter_plays_by_genres(self):
        genre1 = Genre.objects.create(name="Drama")
        genre2 = Genre.objects.create(name="Comedy")
        play1 = Play.objects.create(title="Funny Show", description="...")
        play2 = Play.objects.create(title="Tragedy", description="...")
        play1.genres.add(genre1)
        play2.genres.add(genre2)

        res = self.client.get(PLAY_URL, {"genres": str(genre1.id)})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 1)
        self.assertEqual(res.data["results"][0]["title"], play1.title)

    def test_filter_plays_by_actors(self):
        actor1 = Actor.objects.create(first_name="Emma", last_name="Stone")
        actor2 = Actor.objects.create(first_name="Ryan", last_name="Gosling")
        play1 = Play.objects.create(title="Romantic One", description="...")
        play2 = Play.objects.create(title="Romantic Two", description="...")
        play1.actors.add(actor1)
        play2.actors.add(actor2)

        res = self.client.get(PLAY_URL, {"actors": str(actor1.id)})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 1)
        self.assertEqual(res.data["results"][0]["title"], play1.title)


class PrivatePlayApiTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_superuser(
            "admin@example.com",
            "testpass123"
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_create_play(self):
        genre = sample_genre()
        actor = sample_actor()

        payload = {
            "title": "New Play",
            "description": "Some description",
            "genres": [genre.id],
            "actors": [actor.id]
        }
        res = self.client.post(PLAY_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Play.objects.filter(title=payload["title"]).exists())

    def test_retrieve_play_detail(self):
        play = Play.objects.create(title="Detail Show", description="Detail desc")
        url = detail_url(play.id)

        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["title"], play.title)

    def test_upload_image_to_play(self):
        play = Play.objects.create(title="Image Test", description="Image desc")
        url = upload_image_url(play.id)

        with tempfile.NamedTemporaryFile(suffix=".jpg") as image_file:
            image = Image.new("RGB", (100, 100))
            image.save(image_file, format="JPEG")
            image_file.seek(0)
            res = self.client.post(url, {"image": image_file}, format="multipart")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        play.refresh_from_db()
        self.assertIn("image", res.data)
        self.assertTrue(os.path.exists(play.image.path))

    def test_upload_image_not_admin(self):
        user = get_user_model().objects.create_user(
            "user@example.com",
            "testpass123"
        )
        self.client.force_authenticate(user)
        play = Play.objects.create(title="Unauthorized Upload", description="")
        url = upload_image_url(play.id)

        with tempfile.NamedTemporaryFile(suffix=".jpg") as image_file:
            image = Image.new("RGB", (100, 100))
            image.save(image_file, format="JPEG")
            image_file.seek(0)
            res = self.client.post(url, {"image": image_file}, format="multipart")

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
