from django.shortcuts import render, redirect
from django.http import HttpResponseNotFound, HttpResponse
from django.contrib.auth.decorators import login_required
from . import models
from . import settings
from binascii import hexlify

def index(request, section):
    part = {
        '': 1,
        'part2-download': 2,
        'part3-streaming': 3,
    }[section]
    template = 'part%d.html' % part

    if request.user.is_authenticated():
        part = ''
        profile = models.Profile.get(request.user)

        torrent = models.Torrent.get(request.user, 'lorem.txt', part)

        tracker_url = profile.get_tracker_url(part)
        return render(request, template, {
            'tracker_url': tracker_url,
            'info_hash': hexlify(torrent.info_hash)[:8]})
    else:
        return render(request, template)

def redirect_to_front(request):
    return redirect('/')

@login_required
def log(request):
    return render(request, 'log.html', {
        'logs': models.LogEntry.objects.filter(user=request.user).order_by('-timestamp')[:100]
    })

@login_required
def torrent(request, part, name):
    if name not in ['lorem.txt', 'Xbox-4.avi']:
        return HttpResponseNotFound()
    torrent_obj = models.Torrent.get(request.user, name, part)
    return HttpResponse(torrent_obj.encode(), content_type='application/octet-stream')

def push_log(request):
    info_hash = request.REQUEST['info_hash']
    msg = request.REQUEST['msg']
    torrent = models.Torrent.objects.get(info_hash=info_hash)
    models.LogEntry.log(user=torrent.user, module='client', text=msg)
    return HttpResponse('ok')

def torrent_file(request):
    info_hash = request.REQUEST['info_hash']
    part = request.REQUEST['part']
    torrent = models.Torrent.objects.get(info_hash=info_hash)
    torrent_obj = models.Torrent.get(torrent.user, torrent.name, part)

    return HttpResponse(torrent_obj.encode(), content_type='application/octet-stream')

def torrent_data(request):
    info_hash = request.REQUEST['info_hash']
    try:
        torrent = models.Torrent.objects.get(info_hash=info_hash)
    except models.Torrent.DoesNotExist:
        return HttpResponseNotFound()
    else:
        return HttpResponse(torrent.get_data(), content_type='application/octet-stream')
