import orm
import asyncio
import time
import sys
from models import User,Blog,Comment

def test(loop):
    yield from orm.create_pool(loop=loop,user='root',password='123',database='awesome')
    u=User(name='Test04',email='test04@example.com',passwd='1234567890',image='about:blank')
    yield from u.save()

loop = asyncio.get_event_loop()
loop.run_until_complete(test(loop))
print('test')
print('success')
loop.close()
if loop.is_closed():
    sys.exit(0)
