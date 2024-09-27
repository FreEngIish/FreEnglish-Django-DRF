from django.contrib.auth import get_user_model
from django.utils import timezone


User = get_user_model()

class UserService:
    """
    Service class for handling user creation and retrieval based on Google
    OAuth 2.0 information.

    This class provides functionality to create a new user or retrieve an
    existing user from the database based on the Google subject identifier
    (google_sub). It also updates the user's last login time if the user
    already exists.

    Methods:
        get_or_create_user(google_sub, email, user_info):
            Retrieves an existing user or creates a new user with the provided
            Google information.
    """

    def get_or_create_user(self, google_sub, email, user_info):
        """
        Retrieves a user by their Google subject identifier (google_sub) or
        creates a new user if one does not exist.

        Args:
            google_sub (str): The unique identifier for the user provided by Google.
            email (str): The email address of the user.
            user_info (dict): A dictionary containing user information from Google,
                              including 'given_name' and 'family_name'.

        Returns:
            tuple: A tuple containing:
                - User: The user instance retrieved or created.
                - bool: True if a new user was created, False if an existing
                  user was retrieved.
        """
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
