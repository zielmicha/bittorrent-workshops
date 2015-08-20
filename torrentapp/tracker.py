from django.http import HttpResponse
from django.conf import settings
from . import models

import urllib_raw
import bencode
import ipaddress
import struct
import traceback

def announce(request, tracker_id):
    user = models.Profile.objects.get(tracker_token=tracker_id).user

    try:
        return announce_inner(request, user, tracker_id)
    except Exception as exc:
        traceback.print_exc()
        models.LogEntry.log(user, 'tracker', 'error: %r' % exc)
        raise

def announce_inner(request, user, tracker_id):

    args = urllib_raw.urldecode(request.META['QUERY_STRING'].encode('utf8'))
    print(args)
    info_hash = args[b'info_hash']
    peer_id = args[b'peer_id']

    models.LogEntry.log(user, 'tracker', 'request from %r' % peer_id)

    data = [
        (None, (settings.SELF_IP, settings.CLIENT_PORT)),
    ]

    event = args.get(b'event')
    info = (request.META['REMOTE_ADDR'], int(args[b'port']))
    if event != b'stopped' and peer_id.startswith(b'-TR'):
        models.LogEntry.log(user, 'tracker', 'correct tracker request %s:%d peerid %s' % (
            info[0], info[1], peer_id))
        # data[info_hash][peer_id] = info


    resp = bencode.encode({
        b'interval': 10,
        b'peers': b''.join([
            ipaddress.IPv4Address(this_info[0]).packed
            + struct.pack('!H', this_info[1])
            for this_peer_id, this_info in data
            if this_peer_id != peer_id
        ])
    })

    return HttpResponse(resp, content_type='application/octet-stream')
