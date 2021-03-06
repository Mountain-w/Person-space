from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from comments.models import Comment
from comments.api.serializers import (
CommentSerializer,
CommentSerializerForCreate,
CommentSerializerForUpdate,
)
from utils.decorators import required_params
from comments.api.permissions import IsObjectOwner

class CommentViewSet(viewsets.GenericViewSet):
    """
    只实现 list, create, update, destroy
    不实现 retrieve
    """
    serializer_class = CommentSerializerForCreate
    queryset = Comment.objects.all()
    filterset_fields = ('dynamic_id',)

    def get_permissions(self):
        if self.action == 'create':
            return (IsAuthenticated(),)
        if self.action in ['destroy', 'update']:
            return [IsAuthenticated(), IsObjectOwner()]
        return (AllowAny(),)

    @required_params(params=['dynamic_id'])
    def list(self, request, *args, **kwargs):
        # if 'dynamic_id' not in request.query_params:
        #     return Response({
        #         'message': 'miss dynamic_id in request',
        #         'success':False
        #     }, status=status.HTTP_400_BAD_REQUEST)
        query_set = self.get_queryset()
        comments_ = self.filter_queryset(query_set).order_by('created_at')
        serializer = CommentSerializer(comments_, many=True, context={'request':request})
        return Response(
            {
                'comments': serializer.data
            },
            status=status.HTTP_200_OK
        )

    def create(self, request, *args, **kwargs):
        data = {
            'user_id': request.user.id,
            'dynamic_id': request.data.get('dynamic_id'),
            'content': request.data.get('content'),
        }
        serializer = CommentSerializerForCreate(data=data)
        if not serializer.is_valid():
            return Response({
                'message': "Please check input",
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)
        comment = serializer.save()
        return Response(
            CommentSerializer(comment, context={'request':request}).data,
            status=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        # get_object 是DRF包装的一个函数，会在找不到的时候raise 404 error
        serializer = CommentSerializerForUpdate(
            instance=self.get_object(),
            data=request.data
        )
        if not serializer.is_valid():
            return Response({
                'message': 'please check input',
                'error': serializer.errors,
            },status=status.HTTP_400_BAD_REQUEST)
        # save 方法会触发 serializer 里的 update 方法，点进 save 的具体实现里可以看到
        # save 是根据 instance 参数有没有传来决定是触发 create 还是 update
        comment = serializer.save()
        return Response(CommentSerializer(comment, context={'request':request}).data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        comment = self.get_object()
        comment.delete()
        # DRF 里默认 destroy 返回的是 status code = 204 no content
        # 这里 return 了 success=True 更直观的让前端去做判断，所以 return 200 更合适
        return Response({'success': True}, status=status.HTTP_200_OK)