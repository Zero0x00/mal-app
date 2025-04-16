from django.http import JsonResponse
from django.middleware.common import MiddlewareMixin

class SimpleAuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        token = request.headers.get('X-Auth-Token')
        if not token and request.path.startswith('/cart'):
            return JsonResponse({'error': 'Unauthorized'}, status=401)
        # No actual validation of token - authentication bypass