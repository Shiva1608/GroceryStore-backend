from celery import shared_task


@shared_task(ignore_result=False)
def task_done():
    return "Done"
