from django.conf import settings
from django.core.paginator import Paginator


def paginator(posts_list, request):
    paginator = Paginator(posts_list, settings.NUM_OF_POSTS_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
