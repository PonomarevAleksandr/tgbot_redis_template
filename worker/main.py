import json
import traceback

import asyncio
import uuid
from multiprocessing import Process

from shared.db import rdb


async def get_task(worker_id: str):
    try:

        destination_queue = f"tasks:processing:{worker_id}"
        task_data = rdb.brpoplpush(f'tasks', destination_queue, 0)

        if task_data:

            task = json.loads(task_data.decode())
            lock_key = f"lock-{task['task_id']}"
            acquired_lock = rdb.set(lock_key, worker_id, nx=True, ex=10)

            if acquired_lock:
                rdb.delete(lock_key)
                rdb.lrem(destination_queue, 1, task_data)
                return task

    except Exception as e:
        print(e, traceback.format_exc())

    return None

def worker(worker_id: str):
    async def worker_async(worker_id: str):
        while True:
            task = await get_task(worker_id)
            if task:
                ...



    asyncio.run(worker_async(worker_id))


if __name__ == '__main__':

    processes = []

    for i in range(10):
        worker_id = str(uuid.uuid4().hex)
        processes.append(Process(target=worker, args=(worker_id,)))

    try:
        for p in processes:
            p.start()
        for p in processes:
            p.join()
    except KeyboardInterrupt:
        for p in processes:
            p.terminate()