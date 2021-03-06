from django.urls import reverse
from freezegun import freeze_time

from server.notebooks.models import NotebookRevision


@freeze_time('2018-07-01 13:00')
def test_read_notebook_revisions(fake_user, two_test_notebooks, client):
    test_notebook = two_test_notebooks[0]
    # add two revisions for the main notebook that we are testing
    notebook_revisions = []
    for i in range(2):
        notebook_revisions.append(
            NotebookRevision.objects.create(notebook=test_notebook,
                                            title="Revision %s" % i,
                                            content="*fake notebook content %s*" % i)
        )
        freeze_time('2018-07-01 14:00')

    # add a revision for another notebook, to make sure that doesn't get mixed in
    NotebookRevision.objects.create(notebook=two_test_notebooks[1],
                                    title="Revision for another notebook",
                                    content="*fake notebook 2 content*")

    # verify that we can list notebook revisions and that we only get what we
    # expect in the expected order (latest first)
    resp = client.get(reverse('notebook-revisions-list', kwargs={'notebook_id': test_notebook.id}))
    assert resp.status_code == 200
    assert resp.json() == [{
        'created': '2018-07-01T13:00:00Z',
        'id': revision.id,
        'title': revision.title
    } for revision in reversed(notebook_revisions)]

    # verify that we can get the details of a single revision as well
    test_revision = NotebookRevision.objects.filter(notebook=test_notebook).first()
    resp = client.get(reverse('notebook-revisions-detail', kwargs={
        'notebook_id': test_notebook.id,
        'pk': test_revision.id
    }))
    assert resp.json() == {
        'content': test_revision.content,
        'created': test_revision.created.isoformat()[:-6] + 'Z',
        'id': test_revision.id,
        'title': test_revision.title
    }


def test_read_revisions_non_existent_notebook(fake_user, test_notebook, client):
    resp = client.get(
        reverse("notebook-revisions-list", kwargs={"notebook_id": test_notebook.id + 1})
    )
    assert resp.status_code == 404


def test_create_notebook_revision_not_logged_in(fake_user, test_notebook, client):

    post_blob = {"title": "My cool notebook",
                 "content": "*modified test content"}

    # should not be able to add a revision if not logged in
    resp = client.post(
        reverse("notebook-revisions-list", kwargs={"notebook_id": test_notebook.id}),
        post_blob,
    )
    assert resp.status_code == 403
    assert NotebookRevision.objects.count() == 0


def test_create_notebook_revision_non_owner(fake_user, fake_user2, test_notebook, client):
    post_blob = {"title": "My cool notebook",
                 "content": "*modified test content"}
    # should not be able to add a revision if not owner of notebook
    client.force_authenticate(user=fake_user2)
    resp = client.post(
        reverse("notebook-revisions-list", kwargs={"notebook_id": test_notebook.id}),
        post_blob,
    )
    assert resp.status_code == 403
    assert NotebookRevision.objects.count() == 0


def test_create_notebook_revision(fake_user, test_notebook, client):
    post_blob = {"title": "My cool notebook",
                 "content": "*modified test content"}

    # should be able to create a revision if we are the owner
    client.force_authenticate(user=fake_user)
    resp = client.post(
        reverse("notebook-revisions-list", kwargs={"notebook_id": test_notebook.id}),
        post_blob,
    )
    assert resp.status_code == 201
    assert NotebookRevision.objects.count() == 1
    notebook_revision = NotebookRevision.objects.first()
    assert notebook_revision.title == post_blob['title']
    assert notebook_revision.content == post_blob['content']
