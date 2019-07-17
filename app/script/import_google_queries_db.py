from app.models import *


def validate_query(query):
    """

    :param query:
    :return:
    """
    return True #TODO: placeholder


def import_queries(file, comment=""):
    with open(file) as fin:
        for line in fin:
            line = line.strip()
            if validate_query(line):
                GoogleQuery.objects.create(text=line, comment="")


def make_batches(batch_size, clear_previous_batch=True):
    if clear_previous_batch:
        GoogleQueryBatch.objects.all().delete()

    all_ids = GoogleQuery.objects.all().values_list('id', flat=True)
    batches = _chunks(all_ids, batch_size)

    for batch in batches:
        GoogleQueryBatch.objects.create(item_ids=json.dumps(batch))


def _chunks(l, n):
    """
        Yield successive n-sized chunks from l.
        credit: https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks
    """
    for i in range(0, len(l), n):
        yield l[i:i + n]


if __name__ == '__main__':
    import_queries("../../queries.txt")
    make_batches(batch_size=10)