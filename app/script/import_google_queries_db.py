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
                GoogleQuery.objects.create(text=line, comment=comment)


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


def import_chris_annotations(file, comment=""):
    with open(file) as fin:
        for line in fin:
            line = line.strip()
            parts = line.split('\t')
            _q = GoogleQuery.objects.create(text=parts[1])
            qid = _q.id

            class_labels = parts[0].split(",")
            class_labels = [lbl.strip().lower() for lbl in class_labels]
            debate_worthy = "debate" in class_labels
            cls_lbls = json.dumps(class_labels)
            anno = GoogleQueryAnnotation.objects.create(author="Chris",
                                                        query_id=qid,
                                                        topic_label=cls_lbls,
                                                        debate_worthy=debate_worthy,
                                                        annotation_time=None)


if __name__ == '__main__':
    import_chris_annotations("../../data/chris_annotations.tsv")
    make_batches(batch_size=10)