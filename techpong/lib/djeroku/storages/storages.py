# -*- coding: utf-8 -*-

from __future__ import absolute_import
from pipeline.storage import PipelineMixin
from django.contrib.staticfiles.storage import CachedFilesMixin
from storages.backends.s3boto import S3BotoStorage


# http://code.larlet.fr/django-storages/issue/149/noauthhandlerfound-at-admin
import os
class FixedS3BotoStorage(S3BotoStorage):
    def _get_access_keys(self):
        access_key = os.environ.get('AWS_ACCESS_KEY_ID')
        secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')

        if access_key and secret_key:
            # Both were provided, so use them
            return access_key, secret_key

        return None, None

#http://django-pipeline.readthedocs.org/en/latest/storages.html
class S3CachedPipelineStorage(PipelineMixin, CachedFilesMixin, FixedS3BotoStorage):
    pass


class S3PipelineStorage(PipelineMixin, FixedS3BotoStorage):
    pass