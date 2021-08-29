class BaseEntity(viewsets.ModelViewSet):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)

    def get_permissions(self):
        self.permission_classes = [IsUser]

        if (self.request.method in ['POST', 'DELETE'] or
                (self.request.method == 'GET' and not bool(self.kwargs))):
            self.permission_classes = [IsBackOffice]

        return super().get_permissions()

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()
