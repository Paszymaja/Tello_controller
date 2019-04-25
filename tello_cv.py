import av
import tellopy
import cv2
import numpy as np
from tracker import Tracker


def main():
    tello = TelloCv()

    for packet in tello.container.demux((tello.vid_stream,)):
        for frame in packet.decode():
            image = tello.process_frame(frame)
            cv2.imshow('tello', image)
            cv2.waitKey(1)


class TelloCv(object):
    def __init__(self):
        self.drone = tellopy.Tello()
        self.init_drone()
        self.drone.takeoff()
        self.container = av.open(self.drone.get_video_stream())
        self.vid_stream = self.container.streams.video[0]
        green_lower = (0, 0, 203)
        green_upper = (222, 178, 255)
        self.tracking = True
        self.track_cmd = ''
        self.speed = 20
        self.tracker = Tracker(self.vid_stream.height, self.vid_stream.width, green_lower, green_upper)

    def init_drone(self):
        self.drone.connect()
        self.drone.start_video()

    def process_frame(self, frame):
        image = cv2.cvtColor(np.array(frame.to_image()), cv2.COLOR_RGB2BGR)
        image = self.tracker.draw_arrows(image)

        distance = 100
        xoff, yoff = self.tracker.track(image)
        cmd = ''
        if self.tracking:
            if xoff < -distance:
                cmd = 'counter_clockwise'
            elif xoff > distance:
                cmd = 'clockwise'
            elif yoff < -distance:
                cmd = 'down'
            elif yoff > distance:
                cmd = 'up'
            else:
                if self.track_cmd is not '':
                    getattr(self.drone, self.track_cmd)(0)
                    self.track_cmd = ''
        if cmd is not self.track_cmd:
            if cmd is not '':
                print(cmd)
                getattr(self.drone, cmd)(self.speed)
                self.track_cmd = cmd

        return image



if __name__ == '__main__':
    main()

