from coffin.shortcuts import HttpResponse
import json


def api_response(success=False, error=None, error_code=None, **kwargs):
    response = kwargs
    response['success'] = success
    if error or error_code:
        response['error'] = error
        response['error_code'] = error_code
    return HttpResponse(json.dumps(response))
