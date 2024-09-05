import logging

from channels.db import database_sync_to_async


logger = logging.getLogger('freenglish')


class UserService:
    @database_sync_to_async
    def get_user_from_token(self, token):
        from accounts.models import User
        from accounts.utils import decode_and_verify_token

        try:
            user_data = decode_and_verify_token(token)
            logger.debug(f'Decoded token data: {user_data}')

            # Use the 'sub' field to find the user. 'sub' give from auth0
            user_id = user_data.get('sub')
            if user_id:
                # Assuming you have a method to find a user by 'sub'
                user = User.objects.get(auth0_sub=user_id)  # Or another suitable method for lookup
                return user
            else:
                logger.error('User ID not found in token data')
                return None
        except ValueError as e:
            logger.error(f'Token validation error: {e}')
            return None
        except User.DoesNotExist:
            logger.error('User does not exist')
            return None
