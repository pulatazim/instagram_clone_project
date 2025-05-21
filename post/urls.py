from django.urls import path
from .views import PostListApiView, PostCreateView, PostRetrieveUpdateDestroyView, PostCommentListView, PostCommentCreateView, \
                    CommentListCreateApiView, PostLikeListView, CommentRetriveView, CommentLikeListView,PostLikeApiView, \
                    CommentLikeApiView

urlpatterns = [
    path('list/', PostListApiView.as_view(), name='post-list'),
    path('create/', PostCreateView.as_view(), name='post-create'),
    path('<uuid:pk>/', PostRetrieveUpdateDestroyView.as_view(), name='post-retrieve'),
    path('<uuid:pk>/likes/', PostLikeListView.as_view(), name='post-comment'),
    path('<uuid:pk>/comments/', PostCommentListView.as_view(), name='post-comment-list'),
    path('<uuid:pk>/comments/create', PostCommentCreateView.as_view(), name='post-comment-create'),
    path("comments/", CommentListCreateApiView.as_view(), name='post-comment-create'),
    path("comments/<uuid:pk>/", CommentRetriveView.as_view(), name='post-comment-retrieve'),
    path("comments/<uuid:pk>/likes/", CommentLikeListView.as_view(), name='post-comment-like'),
    path("<uuid:pk>/create-delete-like/", PostLikeApiView.as_view(), name='post-like-create-delete'),
    path("comments/<uuid:pk>/create-delete-like/", CommentLikeApiView.as_view(), name='post-like-create-delete-like'),

]