# import logging
# from retools.queue import QueueManager

# log = logging.getLogger('doula')
# qm = QueueManager()


# def default_job(task_name):
#     # jobs need json passed to them
#     # they need their id
#     # they need a common format
#     # log files need to follow the key value pair format
#     print 'Task Name: ' + task_name
    
#     log.info('starting default job')
#     log.info('ending default job')


# def start_release_queue():
#     # Define all the jobs to be enqueued here
#     # need a solid way to enqueue a job
#     print 'started enqueue'
#     job_id = qm.enqueue('doula.queue.release_queue:default_job', task_name='example task name')

#     print 'JOB ID: ' + str(job_id)

# if __name__ == '__main__':
#     start_release_queue()
