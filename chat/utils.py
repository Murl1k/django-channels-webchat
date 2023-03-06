def is_ajax(request):
    """Функция проверяет, является ли запрос AJAX"""
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'
