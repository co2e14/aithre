from pymba import Vimba, __version__
from typing import Optional
import cv2
from pymba import Frame
from time import sleep

# this will ONLY work on a windows machine with Vimba SDK installed and 
# connected to the same network as the camera

PIXEL_FORMATS_CONVERSIONS = {
    'BayerRG8': cv2.COLOR_BAYER_RG2RGB,
}

def display_frame(frame: Frame, delay: Optional[int] = 1) -> None:
    """
    Displays the acquired frame.
    :param frame: The frame object to display.
    :param delay: Display delay in milliseconds, use 0 for indefinite.
    """
    print('frame {}'.format(frame.data.frameID))

    # get a copy of the frame data
    image = frame.buffer_data_numpy()

    # convert colour space if desired
    try:
        image = cv2.cvtColor(image, PIXEL_FORMATS_CONVERSIONS[frame.pixel_format])
    except KeyError:
        pass

    # display image
    cv2.imshow('Image', image)
    cv2.waitKey(delay)

if __name__ == '__main__':
    print('Pymba version: {}'.format(__version__))
    print('Vimba C API version: {}'.format(Vimba.version()))

    with Vimba() as vimba:
        # provide camera index or id
        camera = vimba.camera('DEV_000F314EE126')
        print(camera)
        system = vimba.system()
        print(system)
        interface = vimba.interface(0)
        print(interface)

# list camera ids
    with Vimba() as vimba:
        print(vimba.camera_ids())

# # list feature infos
#     with Vimba() as vimba:
#         camera = vimba.camera('DEV_000F314EE126')
#         camera.open()

#         for feature_name in camera.feature_names():
#             feature = camera.feature(feature_name)
#             print(feature.info)

#         camera.close()

# set feature values
    FEATURE_NAME = 'PixelFormat'
    with Vimba() as vimba:
        camera = vimba.camera(0)
        camera.open()

        # read a feature value
        feature = camera.feature(FEATURE_NAME)
        value = feature.value

        # set the feature value (with the same value)
        feature.value = value

        print('"{}" was set to "{}"'.format(feature.name, feature.value))

        camera.close()

    # with Vimba() as vimba:
    #     camera = vimba.camera(0)
    #     camera.open()

    #     # arm the camera and provide a function to be called upon frame ready
    #     camera.arm('Continuous', display_frame)
    #     camera.start_frame_acquisition()

    #     # stream images for a while...
    #     sleep(15)

    #     # stop frame acquisition
    #     # start_frame_acquisition can simply be called again if the camera is still armed
    #     camera.stop_frame_acquisition()
    #     camera.disarm()

    #     camera.close()