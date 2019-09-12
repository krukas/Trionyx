from trionyx.api.routers import router

from app.testblog.api import TestApi

apiroutes = [
    router('test', TestApi, 'test')
]