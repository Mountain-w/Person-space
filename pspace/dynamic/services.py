from photos.models import Photo

class DynamicService:
    @classmethod
    def create_photos_from_files(cls, dynamic, files):
        photos = []
        for index, file in enumerate(files):
            photo = Photo(
                dynamic=dynamic,
                user=dynamic.user,
                file=file
            )
            photos.append(photo)
        Photo.objects.bulk_create(photos)