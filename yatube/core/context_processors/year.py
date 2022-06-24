from django.utils import timezone


def year(request):
    a = timezone.now()
    return {'year': int(a.strftime('%Y'))}
