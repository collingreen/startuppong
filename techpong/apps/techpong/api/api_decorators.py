from django.shortcuts import Http404, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist

from apps.techpong.models import *
from apps.techpong.api.api_tools import api_response_invalid


def api_get(view_func):
    def _api_get(request, *args, **kwargs):
        if request.method != 'GET':
            return HttpResponse(
                    "This endpoint only supports GET requests",
                    status=405
                )
        return view_func(request, *args, **kwargs)
    return _api_get

def api_post(view_func):
    @csrf_exempt
    def _api_post(request, *args, **kwargs):
        if request.method != 'POST':
            return HttpResponse(
                    "This endpoint only supports POST requests",
                    status=405
                )
        return view_func(request, *args, **kwargs)
    return _api_post

def api_endpoint(view_func):
    def _api_check(request, *args, **kwargs):

        data = request.POST if request.method == 'POST' else request.GET

        # require api_account_id
        if 'api_account_id' not in data \
                or data['api_account_id'] == '':
            return api_response_invalid(missing_field='api_account_id')

        # require api_access_key
        if 'api_access_key' not in data or \
                data['api_access_key'] == '':
            return api_response_invalid(missing_field='api_access_key')

        # look for target company with matching access key
        api_account_id = data['api_account_id']
        api_access_key = data['api_access_key']
        try:
            company = Company.objects.get(
                api_account_id = api_account_id,
                api_access_key = api_access_key
            )
        except ObjectDoesNotExist:
            return HttpResponse('Permission Denied', status=403)

        # save info on request for view function
        request.api_info = dict(
                api_account_id=api_account_id,
                api_access_key=api_access_key,
                company=company
            )

        # continue to regular view function
        return view_func(request, *args, **kwargs)
    return _api_check

