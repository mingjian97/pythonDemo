#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
from www import markdown2
from www.config_default import configs

__author__='mingjian'
import hashlib
import re
from aiohttp import web
from www.apis import APIValueError, APIError, APIPermissionError, Page, APIResourceNotFoundError
from www.models import User,Comment,Blog,next_id
import asyncio
from www.coroweb import get,post
import time
import json
from www.models import Blog

COOKIE_NAME= 'awesession'
_COOKIE_KEY=configs['session']['secret']

_RE_EMAIL=re.compile(r'^[a-z0-9\.\-\_]+\@[a-z0-9\-\_]+(\.[a-z0-9\-\_]+){1,4}$')
_RE_SHA1=re.compile(r'^[0-9a-f]{40}$')


# 解密cookie:
@asyncio.coroutine
def cookie2user(cookie_str):
    '''
    Parse cookie and load user if cookie is valid.
    '''
    if not cookie_str:
        return None
    try:
        L = cookie_str.split('-')
        if len(L) != 3:
            return None
        uid, expires, sha1 = L
        if int(expires) < time.time():
            return None
        user = yield from User.find(uid)
        if user is None:
            return None
        s = '%s-%s-%s-%s' % (uid, user.passwd, expires, _COOKIE_KEY)
        if sha1 != hashlib.sha1(s.encode('utf-8')).hexdigest():
            logging.info('invalid sha1')
            return None
        user.passwd = '******'
        return user
    except Exception as e:
        logging.exception(e)
        return None

def check_admin(request):
    if request.__user__ is None or not request.__user__.admin:
        raise APIPermissionError()

def text2html(text):
    lines = map(lambda s: '<p>%s</p>' % s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'), filter(lambda s: s.strip() != '', text.split('\n')))
    return ''.join(lines)

def user2cookie(user,max_age):
    expires=str(int(time.time()+max_age))
    s='%s-%s-%s-%s'%(user.id,user.passwd,expires,_COOKIE_KEY)
    L=[user.id,expires,hashlib.sha1(s.encode('utf-8')).hexdigest()]
    return '-'.join(L)
def get_page_index(page_str):
    p = 1
    try:
        p = int(page_str)
    except ValueError as e:
        pass
    if p < 1:
        p = 1
    return p
'''-----思路： 前端页面带有模板，具体操作响应用后端API处理，然后返回响应的页面'''

@get('/')
def index(*, page='1'):
    page_index = get_page_index(page)
    num = yield from Blog.findNumber('count(id)')
    page = Page(num)
    if num == 0:
        blogs = []
    else:
        blogs = yield from Blog.findAll(orderBy='created_at desc', limit=(page.offset, page.limit))
    return {
        '__template__': 'blogs.html',
        'page': page,
        'blogs': blogs
    }
@get('/register')
def register():
    return{
        '__template__':'register.html'
    }
@get('/signin')
def signin():
    return{
        '__template__':'signin.html'
    }
@get('/signout')
def signout(request):
    referer=request.headers.get('Referer')
    r=web.HTTPFound(referer or '/')
    r.set_cookie(COOKIE_NAME, '-deleted-', max_age=0, httponly=True)
    logging.info('user signed out.')
    return r
@get('/blog/{id}')
def get_blog(id):
    blog = yield from Blog.find(id)
    comments = yield from Comment.findAll('blog_id=?', [id], orderBy='created_at desc')
    for c in comments:
        c.html_content = text2html(c.content)
    blog.html_content = markdown2.markdown(blog.content)
    return {
        '__template__': 'blog.html',
        'blog': blog,
        'comments': comments
    }

'''----------------管理员页面------------------------------------------------'''

#返回重定向url ===> manage/comments
@get('/manage/')
def manage():
        return 'redirect:/manage/comments'

#管理评论列表页
@get('/manage/comments')
def manage_comments(*,page='1'):
    return {
        '__template__':'manage_comments.html',
        'page_index':get_page_index(page)
    }

#博客列表页
@get('/manage/blogs')
def manage_blogs(*,page='1'):
    return {
        '__template__':'manage_blogs.html',
        'page_index':get_page_index(page)
    }

#创建博客页，action ===> /api/blogs
@get('/manage/blogs/create')
def manage_create_blog():
    return {
        '__template__': 'manage_blog_edit.html',
        'id': '',
        'action': '/api/blogs'
    }

#修改某篇博客页，action ===> /api/blogs/{id}
@get('/manage/blogs/edit')
def manage_edit_blog(*,id):
    return {
        '__template__':'manage_blog_edit.html',
        'id':id,
        'action':'/api/blogs/%s'%id
    }
#用户列表页
@get('/manage/users')
def manage_users(*,page='1'):
    return{
        '__template__':'manage_users.html',
        'page_index':get_page_index(page)
    }

#管理个人资料
@get('/personal/edit')
async def edit_users():
    return {
        '__template__':'user_edit.html'
    }

#-------------------------------------后端api----------------------------------------

#获取评论
@get('/api/comments')
async def api_comments(*,page='1'):
    page_index=get_page_index(page)
    num=await Comment.findNumber('count(id)')
    p=Page(num,page_index)
    if num==0:
        return dict(page=p,comments=())
    comments=await Comment.findAll(orderby='created_at desc',limit=(p.offset,p.limit))
    return dict(page=p,comments=comments)

#删除评论，需要检查是否有权限
@post('/api/comments/{id}/delete')
async def api_delete_comments(id,request):
    check_admin(request)
    c=await Comment.find(id)
    if c is None:
        raise APIResourceNotFoundError('Comment')
    await c.remove()
    return dict(id=id)
#创建某篇博客的评论
@post('/api/blogs/{id}/comments')
async def api_create_comment(id,request,*,content):
    user=request.__user__
    if user is None:
        raise APIPermissionError('please signin first')
    if not content or not content.strip():
        raise APIValueError('content')
    blog=await Blog.find(id)
    if blog is None:
        raise APIResourceNotFoundError('Blog')
    comment=Comment(blog_id=blog.id,user_id=user.id,user_name=user.name,user_image=user.image,content=content.strip())
    await comment.save()
    return comment

#获取博客
@get('/api/blogs')
def api_blogs(*,page='1'):
    page_index=get_page_index(page)
    num=yield from Blog.findNumber('count(id)')
    p=Page(num,page_index)
    if num==0:
        return dict(page=p,blogs=())
    blogs=yield from Blog.findAll(orderBy='created_at desc',limit=(p.offset,p.limit))
    return dict(page=p,blogs=blogs)
# 获取某篇博客
@get('/api/blogs/{id}')
def api_get_blog(*, id):
    blog = yield from Blog.find(id)
    return blog
#修改某篇博客，由上面 /manage/blogs/edit中action跳转处理
@post('/api/blogs/{id}')
async def api_update_blog(id,request,*,name,summary,content):
    check_admin(request)
    if not name or not name.strip():
        raise APIValueError('name','name cannot be empty')
    if not summary or not summary.strip():
        raise APIValueError('summary','summary cannot be empty')
    if not content or not content.strip():
        raise APIValueError('content','content cannot be empty')
    blog = await Blog.find(id)
    blog.name=name.strip()
    blog.summary=summary.strip()
    blog.content=content.strip()
    await blog.update()
    return blog
#删除某篇博客
@post('/api/blogs/{id}/delete')
async def api_delete_blog(request,*,id):
    check_admin(request)
    blog=await Blog.find(id)
    await blog.remove()
    return dict(id=id)

#创建博客，由/manage/blogs中的action跳转处理
@post('/api/blogs')
def api_create_blog(request,*,name,summary,content):
    check_admin(request)
    if not name or not name.strip():
        raise APIValueError('name','summary cannot be empty')
    if not summary or not summary.strip():
        raise APIValueError('summary','summary cannot be empty')
    if not content or not content.strip():
        raise APIValueError('content','content cannot be empty')
    blog=Blog(user_id=request.__user__.id,user_name=request.__user__.name,
              user_image=request.__user__.image,name=name.strip(),summary=summary.strip(),
              content=content.strip()
              )
    yield from blog.save()
#登陆验证邮箱与密码是否正确，由登陆页get/signin中的action跳转至此处理
@post('/api/authenticate')
def authentication(*,email,passwd):
    if not email:
        raise APIValueError('email','Invalid email.')
    if not passwd:
        raise APIValueError('passwd','Invalid password')
    users=yield from  User.findAll('email=?',[email])
    if len(users)<0:
        raise APIValueError('email','Email not exist')
    user=users[0]
    sha1=hashlib.sha1()
    sha1.update(user.id.encode('utf-8'))
    sha1.update(b':')
    sha1.update(passwd.encode('utf-8'))
    if user.passwd!=sha1.hexdigest():
        raise APIValueError('passwd','Invalid password')
    r=web.Response()
    r.set_cookie(COOKIE_NAME,user2cookie(user,86400),max_age=86400,httponly=True)
    user.passwd='******'
    r.content_type='application/json'
    r.body=json.dumps(user,ensure_ascii=False).encode('utf-8')
    return r

#获取用户
@get('/api/users')
def api_get_users():
    users = yield from User.findAll(orderBy='created_at desc')
    for u in users:
        u.passwd = '******'
    return dict(users=users)

#注册页面时需要填写的信息：邮箱，用户名，密码
@post('/api/users')
def api_register_user(*,email,name,passwd):

    if not name or not name.strip():
        raise APIValueError('name')
    if not email or not _RE_EMAIL.match(email):
        raise APIValueError('email')
    if not passwd or not _RE_SHA1.match(passwd):
        raise APIValueError('passwd')

    users=yield from User.findAll('email=?',[email])

    if len(users)>0:
        raise APIError('register:failed','email','Email is already in use')

    uid=next_id()
    sha1_passwd='%s:%s'%(uid,passwd)
    user=User(id=uid,name=name.strip(),email=email,
              passwd=hashlib.sha1(sha1_passwd.encode('utf-8')).hexdigest(),
              image='http://www.gravator.com/avatar/%s?d=mm&s=120'%hashlib.md5(email.encode('utf-8')).hexdigest())
    yield from user.save()

    r=web.Response()
    r.set_cookie(COOKIE_NAME,user2cookie(user,86400),max_age=86400,httponly=True)
    user.passwd='******'
    r.content_type='application/json'
    r.body=json.dumps(user,ensure_ascii=False).encode('utf-8')
    return r

@post('/api/update_user')
async def api_update_user(*,id,name,oldpasswd,newpasswd):
    if not name or not name.strip():
        raise APIValueError('name')
    if not oldpasswd or not oldpasswd.strip():
        raise APIValueError('oldpasswd')
    if not newpasswd or not newpasswd.strip():
        raise APIValueError('newpasswd')
    user=await User.find(id)
    sha1=hashlib.sha1()
    sha1.update(id.encode('utf-8'))
    sha1.update(b':')
    sha1.update(oldpasswd.encode('utf-8'))
    if user.passwd!=sha1.hexdigest():
        raise APIValueError('passwd','原密码输入错误')
    user.name=name.strip()
    sha1_passwd='%s:%s'%(id,newpasswd)
    user.passwd=hashlib.sha1(sha1_passwd.encode('utf-8')).hexdigest()
    await user.update()
    r=web.Response()
    r.set_cookie(COOKIE_NAME,user2cookie(user,86400),max_age=86400,httponly=True)
    user.passwd='******'
    r.content_type='application/json'
    r.body=json.dumps(user,ensure_ascii=False).encode('utf-8')
    return r


