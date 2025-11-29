from rest_framework_simplejwt.tokens import RefreshToken


def create_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    refresh['id'] = user.id
    refresh['role'] = user.role
    refresh['full_name'] = user.full_name
    refresh['email'] = user.email

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }
