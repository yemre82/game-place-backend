from rest_framework.response import Response
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response:
        if len(response.data) == 1:
            response_text = next(iter(response.data.values()))
            if isinstance(response_text, list):
                return_text = response_text[0]
            else:
                return_text = response_text
            return Response({
                "error": True,
                "errorMsg": return_text,
                "data": None,
            }, response.status_code)
        else:
            return Response({
                "error": True,
                "errorMsg": response.data,
                "data": None
            }, response.status_code)
    else:
        return 