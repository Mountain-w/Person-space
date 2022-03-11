from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from dynamic.api.serializers import DynamicSerializer, DynamicWithComment, DynamicCreateSerializer
from dynamic.models import Dynamic
from newsfeeds.services import NewsFeedService

class DynamicViewset(viewsets.GenericViewSet,
              viewsets.mixins.CreateModelMixin,
              viewsets.mixins.ListModelMixin):
    queryset = Dynamic.objects.all()
    serializer_class = DynamicSerializer

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return (AllowAny(),)
        return (IsAuthenticated(),)

    def retrieve(self, request, *args, **kwargs):
        dynamic = self.get_object()
        return Response({
            'dynamics':DynamicWithComment(dynamic).data
        }, status=200)

    def list(self, request, *args, **kwargs):
        """
        重载 list 方法，不列出全部的动态，这里列出用户的动态
        """
        if 'user_id' not in request.query_params:
            return Response("missing user_id", status=400)
        # 这句查询会被翻译为
        # select * from pspace_dynamic
        # where user_id = xxx
        # order by created_at desc
        # 这句 SQL 查询会用到 user 和 created_at 的联合索引
        # 单纯的 user 索引是不够的
        dynamics = Dynamic.objects.filter(
            user_id=request.query_params['user_id']
        ).order_by('-created_at')
        serializer = DynamicSerializer(dynamics, many=True)
        return Response({"Dynamics": serializer.data})

    def create(self, request, *args, **kwargs):
        """
        重载 create 方法，因为需要默认用当前登录用户作为动态用户
        """
        serializer = DynamicCreateSerializer(
            data=request.data,
            context={"request":request},
        )
        if not serializer.is_valid():
            return Response({
                "success" :False,
                "message": "Please check input",
                "errors": serializer.errors,
            }, status=400)
        dynamic = serializer.save()
        NewsFeedService.fanout_to_followers(dynamic)
        return Response(DynamicSerializer(dynamic).data, status=201)
