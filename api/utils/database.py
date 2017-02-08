from django.db import connection


def delete_all(model):
    '''
    Quickly delete all rows from the database table associated to a model.  This
    uses an inconditional SQL delete statement, which should be considerably
    faster than a manual loop through the ORM like Model.objects.all().delete().
    Note that this will not emit any signals for the deleted model instances,
    but it will fire database triggers on the affected table.
    '''

    cursor = connection.cursor()
    cursor.execute(
        f'delete from "{model._meta.db_table}"',
    )
