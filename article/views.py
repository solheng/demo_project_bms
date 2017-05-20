from flask import request,render_template,redirect,url_for
from flask import Blueprint
from flask.views import MethodView


article = Blueprint('article',__name__)

#@article.route('/articles/')
#def article_list():
#    return render_template('article-list.html')

#@article.route('/articles/<id>/')
#def article_detail(id=None):
#    item = { 'id' : id }
#    return render_template('article-detail.html',item=item)


class ArticleListView(MethodView):
    def get(self):
        return render_template('article-list.html')

    def post(self):
        pass


class ArticleDetailView(MethodView):
    def get(self,id=None):
        item = {'id': id}
        return render_template('article-detail.html', item=item)

article.add_url_rule('/',view_func=ArticleListView.as_view('article_list'))
article.add_url_rule('/<int:id>/',view_func=ArticleDetailView.as_view('article_detail'))



