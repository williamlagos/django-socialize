from django.http import JsonResponse


class ActivityPubHandler:
    def handle_get(self, request, *args, **kwargs):
        # Handle GET requests for ActivityPub
        return JsonResponse({'status': 'GET request received'})

    def handle_post(self, request, *args, **kwargs):
        # Handle POST requests for ActivityPub
        return JsonResponse({'status': 'POST request received'})
