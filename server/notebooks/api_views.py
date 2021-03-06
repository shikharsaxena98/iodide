from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import Http404
from rest_framework import (permissions,
                            viewsets)

from .models import (Notebook, NotebookRevision)
from .serializers import (NotebookDetailSerializer,
                          NotebookListSerializer,
                          NotebookRevisionSerializer,
                          NotebookRevisionDetailSerializer)


class NotebookViewSet(viewsets.ModelViewSet):

    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    # modifying a notebook doesn't make sense once created (if you want to
    # change the title, add a revision doing just that)
    http_method_names = ['get', 'post', 'head', 'delete']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return NotebookDetailSerializer
        return NotebookListSerializer

    def perform_destroy(self, instance):
        if instance.owner != self.request.user:
            raise PermissionDenied
        viewsets.ModelViewSet.perform_destroy(self, instance)

    def perform_create(self, serializer):
        with transaction.atomic():
            notebook = serializer.save(owner=self.request.user)
            NotebookRevision.objects.create(
                notebook=notebook,
                title=self.request.data['title'],
                content=self.request.data['content'])

    queryset = Notebook.objects.all()


class NotebookRevisionViewSet(viewsets.ModelViewSet):

    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    # revisions should be considered immutable once created
    http_method_names = ['get', 'post', 'head']

    def get_serializer_context(self):
        notebook_id = int(self.kwargs['notebook_id'])
        if not Notebook.objects.filter(id=notebook_id).exists():
            raise Http404("Notebook with id %s does not exist" % notebook_id)
        return {'notebook_id': notebook_id}

    def get_queryset(self):
        return NotebookRevision.objects.filter(
            notebook_id=self.kwargs['notebook_id'])

    def get_serializer_class(self):
        if self.action == 'list':
            return NotebookRevisionSerializer
        return NotebookRevisionDetailSerializer

    def perform_create(self, serializer):
        ctx = self.get_serializer_context()
        notebook_owner_id = Notebook.objects.values_list(
            'owner', flat=True).get(id=ctx['notebook_id'])
        if self.request.user.id != notebook_owner_id:
            raise PermissionDenied
        serializer.save(**ctx)
