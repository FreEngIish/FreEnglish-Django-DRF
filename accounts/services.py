from django.contrib.auth import get_user_model
from django.utils import timezone


User = get_user_model()

class UserService:
    def get_or_create_user(self, google_sub, email, user_info):
        user, created = User.objects.get_or_create(
            google_sub=google_sub,
            defaults={
                'email': email,
                'username': email.split('@')[0],  # Set username by email
                'first_name': user_info.get('given_name', ''),
                'last_name': user_info.get('family_name', ''),
            }
        )

        if not created:
            # If the user already exists, update last_login
            user.last_login = timezone.now()
            user.save()

        return user, created
