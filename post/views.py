from django.shortcuts import render

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


from .models import Post, PostLike, PostComment, CommentLike
from .serializers import PostSerializer, PostLikeSerializer, CommentSerializer, CommentLikeSerializer
from shared.costom_pagination import CustomPagination


class PostListApiView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [AllowAny, ]
    pagination_class = CustomPagination

    def get_queryset(self):
        return Post.objects.all()


class PostCreateView(generics.CreateAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated, ]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class PostRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, ]

    def put(self, request, *args, **kwargs):
        post = self.get_object()
        serializer = self.serializer_class(post, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        post = self.get_object()
        post.delete()
        return Response({
            "success": True,
            "code": status.HTTP_204_NO_CONTENT,
            "message": "Post successfully deleted",
        })


class PostCommentListView(generics.ListAPIView):
    serializer_class = CommentSerializer
    permission_classes = [AllowAny, ]

    def get_queryset(self):
        post_id = self.kwargs['pk']
        queryset = PostComment.objects.filter(post_id=post_id)
        return queryset


class PostCommentCreateView(generics.CreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, ]

    def perform_create(self, serializer):
        post_id = self.kwargs['pk']
        serializer.save(auther=self.request.user, post_id=post_id)


class CommentListCreateApiView(generics.ListCreateAPIView):
    serializer_class = CommentLikeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, ]
    queryset = PostComment.objects.all()
    pagination_class = CustomPagination

    def perform_create(self, serializer):
        serializer.save(auther=self.request.user)


class CommentRetriveView(generics.RetrieveAPIView):
    serializer_class = CommentLikeSerializer
    permission_classes = [AllowAny, ]
    queryset = PostComment.objects.all()


class PostLikeListView(generics.ListAPIView):
    serializer_class = PostLikeSerializer
    permission_classes = [AllowAny, ]

    def get_queryset(self):
        post_id = self.kwargs['pk']
        return PostLike.objects.filter(post_id=post_id)


class CommentLikeListView(generics.ListAPIView):
    serializer_class = CommentLikeSerializer
    permission_classes = [AllowAny, ]

    def get_queryset(self):
        comment_id = self.kwargs['pk']
        return CommentLike.objects.filter(comment_id=comment_id)


class PostLikeApiView(APIView):

    def post(self, request, pk):
        try:
            post_like = PostLike.objects.get(
                author=self.request.user,
                post_id=pk
            )
            post_like.delete()
            data = {
                "success": True,
                "message": "Layk o'chirildi!",
            }
            return Response(data,  status=status.HTTP_204_NO_CONTENT)
        except Postlike.DoesNotExist:
            post_like = PostLike.objects.create(
                author=self.request.user,
                post_id=pk,
            )
            serializer = PostLikeSerializer(post_like)
            data = {
                "success": True,
                "message": "Layk bosildi!",
                'data': serializer.data
            }
            return Response(data, status=status.HTTP_201_CREATED)

    # Postga layk bosish va uni o'chirish funksiyasi
    # def post(self, request, pk):
    #     try:
    #         post_like = PostLike.objects.create(
    #             author=self.request.user,
    #             post_id=pk,
    #         )
    #         serializer = PostLikeSerializer(post_like)
    #         data = {
    #             "success": True,
    #             "message": "Postga like bosildi!",
    #             "data": serializer.data
    #         }
    #         return Response(data, status=status.HTTP_201_CREATED)
    #     except Exception as e:
    #         data = {
    #             "success": False,
    #             "message": f"{str(e)}",
    #             "data": None,
    #         }
    #         return Response(data, status=status.HTTP_400_BAD_REQUEST)
    #
    # def delete(self, request, pk):
    #     try:
    #         post_like = PostLike.objects.get(
    #             author=self.request.user,
    #             post_id=pk,
    #         )
    #         post_like.delete()
    #         data = {
    #             "success": True,
    #             "message": "Like o'chirildi!",
    #             "data": None
    #         }
    #         return Response(data, status=status.HTTP_200_OK)
    #
    #     except Exception as e:
    #         data = {
    #             "success": False,
    #             "message": f"{str(e)}",
    #             "data": None,
    #         }
    #         return Response(data, status=status.HTTP_400_BAD_REQUEST)


class CommentLikeApiView(APIView):

    def post(self, request, pk):
        try:
            comment_like = CommentLike.objects.get(
                author=self.request.user,
                comment_id=pk
            )
            comment_like.delete()
            data = {
                "success": True,
                "message": "Layk o'chirildi!",
            }
            return Response(data, status=status.HTTP_204_NO_CONTENT)
        except CommentLike.DoesNotExist:
            comment_like = CommentLike.objects.create(
                author=self.request.user,
                comment_id=pk,
            )
            serializer = CommentLikeSerializer(comment_like)
            data = {
                "success": True,
                "message": "Layk bosildi!",
                "data": serializer.data
            }
            return Response(data, status=status.HTTP_201_CREATED)
