from django.http import JsonResponse
from django.middleware.common import MiddlewareMixin

class SimpleAuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.path.startswith('/cart/custom_add/') or request.path.startswith('/cart/view/'):
            token = request.headers.get('X-Auth-Token')
            if not token:
                return JsonResponse({'error': 'Unauthorized'}, status=401)
        # No actual validation of token - authentication bypass
