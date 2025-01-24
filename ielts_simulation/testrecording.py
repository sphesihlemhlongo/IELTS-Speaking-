import pyaudio
import wave

def record_audio(output_file="output.wav", record_seconds=5, sample_rate=44100, channels=1, chunk_size=1024):
    """
    Records audio from the default input device and saves it as a .wav file.
    
    Args:
        output_file (str): The file path to save the audio.
        record_seconds (int): Duration of the recording in seconds.
        sample_rate (int): The sample rate in Hz.
        channels (int): Number of audio channels (1 for mono, 2 for stereo).
        chunk_size (int): Size of audio chunks to read at a time.
    """
    audio = pyaudio.PyAudio()

    # Open a new stream for recording
    stream = audio.open(
        format=pyaudio.paInt16, 
        channels=channels,
        rate=sample_rate,
        input=True,
        input_device_index=1,
        frames_per_buffer=chunk_size
    )

    print(f"Recording for {record_seconds} seconds...")
    frames = []

    # Capture audio data in chunks
    for _ in range(0, int(sample_rate / chunk_size * record_seconds)):
        data = stream.read(chunk_size)
        frames.append(data)

    # Stop the stream and close it
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # Save the recorded audio to a .wav file
    with wave.open(output_file, 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
        wf.setframerate(sample_rate)
        wf.writeframes(b''.join(frames))

    print(f"Recording saved to {output_file}")
# record_audio()

def list_audio_devices():
    audio = pyaudio.PyAudio()
    print("Available Audio Devices:")
    for i in range(audio.get_device_count()):
        device_info = audio.get_device_info_by_index(i)
        print(f"ID {i}: {device_info['name']} (Input Channels: {device_info['maxInputChannels']})")
    audio.terminate()

list_audio_devices()
