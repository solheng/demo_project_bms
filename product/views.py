from flask import render_template
from flask import Blueprint

product = Blueprint('product',__name__)

@product.route('/')
def product_list():
    return '产品列表页'


@product.route('/<int:id>/')
def product_detain(id=None):
    return '产品详情'+ str(id)