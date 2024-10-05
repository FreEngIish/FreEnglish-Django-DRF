import logging

import requests
from channels.db import database_sync_to_async

logger = logging.getLogger('freenglish')


class UserService:
    @database_sync_to_async
    def get_user_from_token(self, token):
        from accounts.models import User
        try:
            response = requests.get(f'https://oauth2.googleapis.com/tokeninfo?access_token={token}')

            if response.status_code == 200:
                user_info = response.json()

                user_email = user_info.get('email')
                if user_email:
                    user = User.objects.get(email=user_email)
                    return user
                else:
                    logger.error('Email not found in token data')
                    return None
            else:
                logger.error(f'Token validation error: {response.content}')
                return None
        except User.DoesNotExist:
            logger.error('User does not exist')
            return None
        except Exception as e:
            logger.error(f'Unexpected error occurred: {e}')
            return None
