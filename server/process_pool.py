from multiprocessing import Lock, Process, Queue, Value

def lobby(queue: Queue, working, working_lock):
    while True:
        try:
            task = queue.get(timeout=1)
        except:
            working_lock.acquire()
            if not working.value:
                working_lock.release()
                break
            working_lock.release()
        f(task)



def create_processes(function, args):
    process_list = []
    queue_list = []
    queue_list.append(Queue())
    queue_list.append(Queue())
    queue_list.append(Queue())
    queue_list.append(Queue())
    queue_list.append(Queue())
    process_list.append(Process(target=lobby, args=(queue_list[0], args)))
    process_list.append(Process(target=lobby, args=(queue_list[1], args)))
    process_list.append(Process(target=lobby, args=(queue_list[2], args)))
    process_list.append(Process(target=lobby, args=(queue_list[3], args)))
    process_list.append(Process(target=lobby, args=(queue_list[4], args)))
    return process_list, queue_list