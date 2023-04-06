import os
import docker
from redis import Redis

from mirrcore.job_queue import JobQueue
from mirrdash.dashboard_server import create_server

mongo_host = os.getenv('MONGO_HOSTNAME')
job_queue = JobQueue(Redis('redis'))
server = create_server(job_queue, docker.from_env())
app = server.app
