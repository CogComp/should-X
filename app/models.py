import datetime
import json
import numpy as np
import random

from abc import abstractmethod

from django.db import models


#############################
#       BASE CLASSES        #
#############################

class AbstractAnnotationSession(models.Model):
    username = models.CharField(max_length=100)
    instruction_complete = models.BooleanField(default=False)
    job_complete = models.BooleanField(default=False)
    jobs = models.TextField()  # a list of integer ids
    finished_jobs = models.TextField()
    duration = models.DurationField()
    last_start_time = models.DateTimeField(null=True) # Used to calculate duration

    class Meta:
        abstract = True

    @classmethod
    @abstractmethod
    def get_batch_class(cls):
        return AbstractBatch.__class__

    @classmethod
    def get_session(cls, username):
        unfinished_sessions = cls.objects.filter(username=username).exclude(job_complete=True)
        if unfinished_sessions.count() > 0:
            session = unfinished_sessions[0]
        else:
            claim_ids = cls.generate_jobs(username, 1)
            time_now = datetime.datetime.now(datetime.timezone.utc)
            session = cls.objects.create(username=username,
                                         jobs=json.dumps(claim_ids),
                                         finished_jobs=json.dumps([]),
                                         instruction_complete=cls.instr_needed(username),
                                         duration=datetime.timedelta(),
                                         last_start_time=time_now)

        return session

    @classmethod
    def clean_idle_sessions(cls, default_timeout_minutes=30):
        sessions = cls.objects.filter(job_complete=0, finished_jobs="[]")
        for s in sessions.iterator():
            last_access_time = s.last_start_time
            time_now = datetime.datetime.now(datetime.timezone.utc)
            elapsed = time_now - last_access_time

            _timeout = datetime.timedelta(minutes=default_timeout_minutes)

            if elapsed > _timeout:
                jobs = json.loads(s.jobs)
                cls.get_batch_class().decrease_assign_counts(jobs)
                s.delete()

    @classmethod
    def instr_needed(cls, username):
        """
        Check if a user need to take instruction
        :param username:
        :return: True if user need to take instruction
        """
        count = cls.objects.filter(username=username, instruction_complete=True).count()
        return count > 0

    @classmethod
    def generate_jobs(cls, username, num_jobs, max_assign_count=3):
        """
        When each worker first login, generate the set of jobs they will be doing
        :param username:
        :param num_jobs: number of jobs for this session
        :param max_assign_count max assignment counts for each batch
        :return:
        """
        cls.clean_idle_sessions()

        finished = cls.get_all_finished_batches(username)

        eb_id_set = cls.get_batch_class().objects.filter(assign_counts__lt=max_assign_count).exclude(id__in=finished)

        if len(eb_id_set) >= num_jobs:
            # Case 1: where we still have claims with lower than 3 assignments
            assign_counts = eb_id_set.values_list('id', 'assign_counts', named=True)\
                .order_by('assign_counts')

            # Add [0, 1) random parts to each assignment counts, for randomly sorting claims with assignment counts
            count_tuples = []
            for c in assign_counts:
                count_tuples.append((c.id, c.assign_counts + random.random()))

            count_tuples = sorted(count_tuples, key=lambda t: t[1])[:num_jobs]

            jobs = [t[0] for t in count_tuples]

        else:
            # Case 2: all claims have been assigned max_assign_count times
            # In such cases, assign the least annotated claims
            assign_counts = cls.objects.all().exclude(id__in=finished).order_by('finished_counts')\
                .values_list('id', 'finished_counts', named=True)[:num_jobs * 5]

            if len(assign_counts) == 0:
                jobs = []
            else:
                jobs = np.random.choice([t.id for t in assign_counts], size=num_jobs, replace=False).tolist()

        if username != "TEST":
            cls.get_batch_class().increment_assign_counts()

        return jobs

    @classmethod
    def get_all_finished_batches(cls, username):
        _jobs = cls.objects.filter(username=username).values_list("jobs", flat=True)
        jobs = []
        for j in _jobs:
            jobs += json.loads(j)

        return jobs


class AbstractBatch(models.Model):

    class Meta:
        abstract = True

    item_ids = models.TextField(default="[]") # serialized json -- list of integer item ids
    assign_count = models.IntegerField(default=0)
    finish_count = models.IntegerField(default=0)

    @classmethod
    def _offset_assign_counts(cls, ids, offset):
        for id in ids:
            batch = cls.objects.get(id=id)
            end_count = batch.assign_count + offset
            if end_count >= 0:
                batch.assign_count = end_count
            else:
                batch.assign_count = 0

            batch.save()

    @classmethod
    def increment_assign_counts(cls, ids):
        return cls._offset_assign_counts(ids, 1)

    @classmethod
    def decrease_assign_counts(cls, ids):
        return cls._offset_assign_counts(ids, -1)

    @classmethod
    @abstractmethod
    def get_item_class(cls):
        return AbstractBatch.__class__


#############################
#      MODEL CLASSES        #
#############################
class GoogleQuery(models.Model):
    text = models.TextField()


class GoogleQueryAnnotation(models.Model):
    author = models.TextField()
    debate_worthy = models.BinaryField()
    topic_label = models.CharField(max_length=50)
    annotation_time = models.DateTimeField()


class GoogleQueryBatch(AbstractBatch):
    @classmethod
    def get_item_class(cls):
        return GoogleQuery.__class__


class GoogleQueryAnnotationSession(AbstractAnnotationSession):
    @classmethod
    def get_batch_class(cls):
        return GoogleQueryBatch.__class__






