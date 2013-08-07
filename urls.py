from django.conf.urls import patterns, include, url
import settings

urlpatterns = patterns('',
	url(r'^$', 'app.portfolio.views.get_page'),
	url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root':settings.STATIC_ROOT,}),
)
