import sys
import soundfile as sf
from tqdm import tqdm
from discontinuity_detector.utils import utils
from discontinuity_detector.utils.dsp import calc_abs_derivative


class DiscontinuityDetectorFile:
    def __init__(self, file_path, threshold: float = 0.1):
        self.file_path = file_path
        self.file = None
        self.file_info: sf._SoundFileInfo = None
        self.blocksize: int = 0
        self.overlap: int = 0
        self.current_frame: int = 0
        self.discontinuities: list[int] = []
        self.threshold = threshold

        self.banner()
        print(f"Detecting discontinuities in file: {self.file_path}")

    def banner(self):
        print("-----------------------------------------------------------------------")

    def open_file(self):
        """Open the .wav file"""
        try:
            self.file = sf.SoundFile(self.file_path)
            self.file_info = sf.info(self.file_path)
            self.blocksize = self.file_info.samplerate
            self.overlap = int(self.file_info.samplerate / 1000)
        except Exception as e:
            print(f"ERROR: {e}")
            self.banner()
            sys.exit(1)

    def _process_block(self, block):
        # Create an ndarray for each channel
        if self.file_info.channels > 1:
            samples = block.T
        else:
            samples = block.reshape(1, -1)

        abs_deriv = calc_abs_derivative(samples)
        block_discont = utils.count_discontinuities(abs_deriv, threshold=self.threshold)

        for channel in range(self.file_info.channels):
            for discont in block_discont[channel]:
                # Convert to absolute frame number
                abs_frame = discont + self.current_frame
                self.discontinuities.append(abs_frame)

        # Update next block start time
        self.current_frame += self.blocksize - self.overlap

    def process_file(self) -> list[int]:
        """Process the file in blocks, with a progress bar showing the estimated frames left."""
        if self.file is None:
            print("File is not open. Call open_file() first.")
            return

        total_frames = self.file_info.frames
        block_count = int(total_frames / (self.blocksize - self.overlap)) + 1

        try:
            with tqdm(total=block_count, desc="Processing", unit="block") as pbar:
                for block in sf.blocks(self.file_path, blocksize=self.blocksize, overlap=self.overlap):
                    self._process_block(block)
                    pbar.update(1)  # Update the progress bar by one block
        except Exception as e:
            print(f"Error processing blocks: {e}")

        # remove duplicates and sort low to high
        self.discontinuities = list(set(self.discontinuities))
        self.discontinuities.sort()
        return self.discontinuities

    def show_results(self):
        self.banner()
        print("Number of discontinuities detected: ", len(self.discontinuities))
        for disc in self.discontinuities:
            ms = utils.get_time_ms(disc, self.file_info.samplerate)
            print(utils.format_ms(ms))
        self.banner()

    def close_file(self):
        """Close the file"""
        if self.file is not None:
            self.file.close()
            self.file = None

    def __enter__(self):
        """Context manager entry method"""
        self.open_file()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Context manager exit method, ensures file is closed"""
        self.close_file()
