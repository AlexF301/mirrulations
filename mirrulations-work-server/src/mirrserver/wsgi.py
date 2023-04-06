from mirrserver.work_server import create_server
from mirrcore.redis_check import load_redis

database = load_redis()
server = create_server(database)
app = server.app
