from django.contrib import admin
from .models import ChatMessage, Thread, Profile

admin.site.register(ChatMessage)
admin.site.register(Profile)


class ChatMessageAdmin(admin.TabularInline):
    model = ChatMessage

class ThreadAdmin(admin.ModelAdmin):
    inlines = [ChatMessageAdmin]

    class Meta:
        model = Thread


admin.site.register(Thread, ThreadAdmin)
