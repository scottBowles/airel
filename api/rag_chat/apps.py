from django.apps import AppConfig


class RagChatConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "rag_chat"

    def ready(self):
        from .signals import connect_embedding_signals

        connect_embedding_signals()
