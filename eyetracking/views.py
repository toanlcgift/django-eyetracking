from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Room
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.http import Http404, HttpResponseRedirect, StreamingHttpResponse
import cv2
from .gaze_tracking import GazeTracking
import numpy

gaze = GazeTracking()

@login_required(login_url='accounts/login/')
def index(request):
    """
    Root page view. This is essentially a single-page app, if you ignore the
    login and admin parts.
    """
    # Get a list of rooms, ordered alphabetically
    rooms = Room.objects.order_by("title")

    # Render that in the index template
    return render(request, "index.html", {
        "rooms": rooms,
    })

@login_required(login_url='accounts/login/')
def upload_image(request):
        if request.method == 'POST':
              file = request.FILES['data']
              frame = cv2.imdecode(numpy.fromstring(file.read(), numpy.uint8), cv2.IMREAD_UNCHANGED)
              gaze.refresh(frame)

              frame = gaze.annotated_frame()
              text = ""

              if gaze.is_blinking():
                    text = "Blinking"
              elif gaze.is_right():
                    text = "Looking right"
              elif gaze.is_left():
                    text = "Looking left"
              elif gaze.is_center():
                    text = "Looking center"

              cv2.putText(frame, text, (90, 60), cv2.FONT_HERSHEY_DUPLEX, 1.6, (147, 58, 31), 2)

              left_pupil = gaze.pupil_left_coords()
              right_pupil = gaze.pupil_right_coords()
              cv2.putText(frame, "Left pupil:  " + str(left_pupil), (90, 130), cv2.FONT_HERSHEY_DUPLEX, 0.9, (147, 58, 31), 1)
              cv2.putText(frame, "Right pupil: " + str(right_pupil), (90, 165), cv2.FONT_HERSHEY_DUPLEX, 0.9, (147, 58, 31), 1)
              channel_layer = get_channel_layer()
              async_to_sync(channel_layer.group_send)("room-1", 
                {
                    "type": "chat.message",
                    "username": "user",
                    "message": text,
                    "room_id": 1
                })

        return StreamingHttpResponse('POST request')