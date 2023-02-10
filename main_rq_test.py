# from redis import Redis
# from rq import Queue
import redis
import rq
import task

pool = redis.ConnectionPool(host='192.168.1.1', port=6379, db=0, password='JdhskjaWjdk')
redis_conn = redis.Redis(connection_pool=pool)

redis_conn.set('mykey', 'Hello from Python!')
value = redis_conn.get('mykey')
print(value)

queue = rq.Queue(connection=redis_conn)

x = 2
y = 3
job = queue.enqueue(task.slow_multiply, x, y)
print('Job id: %s' % job.id)
print(job.return_value())
