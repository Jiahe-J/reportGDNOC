#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" 
__author__ = silenthz 
__date__ = 2018/9/17
"""
from django.http import JsonResponse
from rest_framework.authentication import SessionAuthentication
from rest_framework.views import APIView
from rest_framework_jwt.authentication import JSONWebTokenAuthentication


class UserInfoView(APIView):
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication,)

    def get(self, request):
        user = self.request.user
        user_data = dict(
            username=user.username,
            email=user.email
        )

        return JsonResponse(data=user_data, safe=False)
