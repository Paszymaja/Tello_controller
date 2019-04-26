import av
import tellopy
import cv2
import numpy as np
from tracker import Tracker
from pynput import keyboard


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
        self.tracking = False
        self.init_drone()
        self.drone.takeoff()
        self.key = False
        self.container = av.open(self.drone.get_video_stream())
        self.vid_stream = self.container.streams.video[0]
        green_lower = (30, 50, 50)
        green_upper = (80, 255, 255)
        self.track_cmd = ''
        self.speed = 20
        self.tracker = Tracker(self.vid_stream.height, self.vid_stream.width, green_lower, green_upper)

    def init_drone(self):
        self.drone.connect()
        self.drone.start_video()
        with keyboard.Listener(on_press=self.on_press, on_release=self.on_release) as Listener:
            Listener.join()

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

    def on_press(self, key):
        if key == keyboard.Key.up and self.tracking is False:
            self.tracking = True
            print('Tracking on')
        elif key == keyboard.Key.up and self.tracking is True:
            self.tracking = False
            print('Tracking off')

    def on_release(self, key):
        if key == keyboard.Key.esc:
            self.drone.land()
            self.drone.quit()
            return False


if __name__ == '__main__':
    main()

