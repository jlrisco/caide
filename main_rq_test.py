# from redis import Redis
# from rq import Queue
import redis
import rq
import task

pool = redis.ConnectionPool(host='34.175.39.166', port=6379, db=0, password='Carmen1975!')
redis_conn = redis.Redis(connection_pool=pool)

redis_conn.set('mykey', 'Hello from Python!')
value = redis_conn.get('mykey')
print(value)

# Create a Redis connection with 34.175.39.166
# redis_conn = Redis(host='34.175.39.166')
queue = rq.Queue(connection=redis_conn)

x = 2
y = 3
job = queue.enqueue(task.slow_multiply, x, y)
print('Job id: %s' % job.id)
print(job.return_value())
