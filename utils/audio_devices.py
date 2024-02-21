from pyaudio import PyAudio


def list_audio_devices():
    p = PyAudio()
    num_devices = p.get_device_count()
    for i in range(num_devices):
        device_info = p.get_device_info_by_index(i)
        print(f"Device {i}: {device_info['name']}")
