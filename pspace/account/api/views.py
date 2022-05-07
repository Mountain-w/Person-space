from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth import (
    authenticate as django_authenticate,
    login as django_login,
    logout as django_logout,
)
from account.api.serializers import UserSerializer, SignupSerializer, LoginSerializer, UserProfileSerializer, UserProfileForUpdate
from utils.auth.authhelper import generate_token


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class AccountViewSet(viewsets.ViewSet):
    permission_classes = (AllowAny,)
    serializer_class = SignupSerializer

    @action(methods=['POST'], detail=False)
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                "success": False,
                "message": "Please check input",
                "errors": serializer.errors,
            }, status=400)
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        user = django_authenticate(username=username, password=password)
        if not user or user.is_anonymous:
            return Response({
                "success": False,
                "message": "username and password does match",
            }, status=400)
        # django_login(request, user)
        request.user = user
        return Response({
            "success": True,
            "user": UserSerializer(instance=user, context={'request':request}).data,
            "token": generate_token(user.username)
        })

    @action(methods=['POST'], detail=False)
    def logout(self, request):
        django_logout(request)
        return Response({"success": True})

    @action(methods=["POST"], detail=False)
    def signup(self, request):
        serializer = SignupSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                "success": False,
                "message": "Please check input",
                "errors": serializer.errors,
            }, status=400)
        user = serializer.save()
        # django_login(request, user)
        request.user = user
        return Response({
            "success": True,
            "user": UserSerializer(user, context={'request':request}).data,
            "token": generate_token(user.username)
        }, status=201)

    @action(methods=["GET"], detail=False)
    def login_status(self, request):
        data = {"has_logged_in": request.user.is_authenticated}
        if request.user.is_authenticated:
            data['user'] = UserSerializer(request.user, context={'request':request}).data
        return Response(data)


class ProfileViewSet(viewsets.GenericViewSet):
    serializer_class = UserProfileSerializer
    queryset = User.objects.all().order_by('-date_joined')

    def retrieve(self, request, pk, *args, **kwargs):
        instance = self.get_object()
        print(instance.profile.id)
        return Response({
            'profile': UserProfileSerializer(instance.profile).data,
        }, status=200)

    def update(self, request, pk, *args, **kwargs):
        print(pk)
        instance = self.get_object()
        if instance != request.user:
            return Response({
                'message': "You can't update other's profile"
            }, status=403)
        serializer = UserProfileForUpdate(
            instance=request.user.profile,
            data={
                "nickname": request.data.get('nickname'),
                "introduction": request.data.get('introduction'),
                "avatar": request.FILES.get('avatar')
            }
        )
        if not serializer.is_valid():
            return Response({
                "message": "Please check your input",
                "errors": serializer.errors,
            }, status=400)
        instance = serializer.save()
        print(instance.avatar.url, instance.nickname)
        return Response({"success": "ok"}, status=201)