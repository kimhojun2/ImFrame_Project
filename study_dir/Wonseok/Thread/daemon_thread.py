import threading
import time


def job(_jobs, _delay, _name):
    print(f"{_name} got {_jobs} jobs")

    for i in range(_jobs):
        print(f"{_name} finished #{i} job")
        time.sleep(_delay)

    print(f"{_name} is leaving")


thread_1 = threading.Thread(target=job, args=(5, 0.1, 'Worker'))
thread_1.start()

thread_2 = threading.Thread(target=job, args=(10, 0.1, "Admin"))
thread_2.daemon = True
thread_2.start()

job(3, 0.1, "Boss")
