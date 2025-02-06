from django.contrib import admin
from .models import Post, PostLike, PostComment, CommentLike


class PostAdmin(admin.ModelAdmin):
    list_display = ('caption', 'author', 'created_time', 'id')
    search_fields = ('id', 'author__username', 'caption')


class PostCommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'comment', 'created_time', 'id')
    search_fields = ('id', 'author__username', 'comment')


class PostLikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'post', 'created_time')
    search_fields = ('id', 'author__username', 'post')


class CommentLikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'comment', 'created_time')
    search_fields = ('id', 'author__username', 'comment')


admin.site.register(Post, PostAdmin)
admin.site.register(PostComment, PostCommentAdmin)
admin.site.register(PostLike, PostLikeAdmin)
admin.site.register(CommentLike, CommentLikeAdmin)
