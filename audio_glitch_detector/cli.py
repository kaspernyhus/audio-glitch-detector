import argparse
import math
import signal
import sys
from threading import Event

from tqdm import tqdm

from . import __version__
from .audio import AudioConfig, FileReader, StreamReader, print_audio_devices, save_glitch_block
from .core import GlitchDetector
from .tui import ConsoleOutput
from .utils import format_time_string


def create_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser."""
    parser = argparse.ArgumentParser(description="Detect audio glitches and discontinuities in sinusoidal signals")
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"audio-glitch-detector {__version__}",
    )
    parser.add_argument(
        "-t",
        "--threshold",
        type=float,
        default=0.12,
        help="discontinuity detection threshold",
    )
    parser.add_argument(
        "-f",
        "--filename",
        help="Audio file to analyze",
    )
    parser.add_argument(
        "-r",
        "--sample_rate",
        type=int,
        default=48000,
        help="Sample rate for stream mode (default: 48000)",
    )
    parser.add_argument(
        "-c",
        "--channels",
        type=int,
        default=2,
        choices=[1, 2],
        help="Number of channels for stream mode (default: 2)",
    )
    parser.add_argument(
        "--bit_depth",
        type=int,
        default=32,
        choices=[16, 32],
        help="Bit depth for stream mode (default: 32)",
    )
    parser.add_argument(
        "--block-size",
        type=int,
        default=1024,
        help="Block size for file processing (default: 1024)",
    )
    parser.add_argument(
        "-s",
        "--save-blocks",
        action="store_true",
        help="Save audio blocks containing glitches as .wav files (default: off)",
    )
    return parser


def run_file_mode(filename: str, threshold: float, block_size: int, save_blocks: bool, output: ConsoleOutput) -> None:
    """Run glitch detection on a file using block-based processing with block overlap."""
    try:
        with FileReader(filename, block_size=1, overlap=0) as temp_reader:
            sample_rate = temp_reader.sample_rate
            channels = temp_reader.channels
            duration = temp_reader.duration_seconds
            total_frames = temp_reader.frames

        overlap = int(block_size / 10)

        output.log(f"Analyzing file: {filename}")
        output.log(f"Sample rate: {sample_rate} Hz")
        output.log(f"Channels: {channels}")
        output.log(f"Duration: {duration:.2f} seconds")
        output.log(f"Block size: {block_size} samples")
        output.log(f"Overlap: {overlap} samples")

        total_block_count = math.ceil(total_frames / (block_size - overlap))

        with FileReader(filename, block_size=block_size, overlap=overlap) as reader:
            detector = GlitchDetector(reader.sample_rate, threshold)

            all_glitch_indices = []
            all_glitch_timestamps = []

            # Process blocks with progress bar
            with tqdm(total=total_block_count, desc="Processing", unit="block") as pbar:
                for samples, frame_offset in reader.read_blocks():
                    result = detector.detect_with_offset(samples, frame_offset)

                    all_glitch_indices.extend(result.sample_indices)
                    all_glitch_timestamps.extend(result.timestamps_ms)

                    if save_blocks and result.total_count > 0:
                        save_glitch_block(samples, reader.sample_rate, frame_offset, threshold)

                    pbar.update(1)

            unique_indices = sorted(set(all_glitch_indices))
            unique_timestamps = [format_time_string(detector._sample_to_milliseconds(idx)) for idx in unique_indices]

            output.print_results(len(unique_indices), unique_timestamps)

    except Exception as e:
        output.log(f"Error processing file: {e}", style="bold red")
        sys.exit(1)


def run_stream_mode(config: AudioConfig, threshold: float, save_blocks: bool, output: ConsoleOutput) -> None:
    """Run real-time glitch detection on audio stream."""
    exit_event = Event()
    glitch_count = 0

    def signal_handler(sig, frame):
        exit_event.set()

    def glitch_callback(samples, frame_number):
        nonlocal glitch_count
        detector = GlitchDetector(config.sample_rate, threshold)
        result = detector.detect_with_offset(samples, frame_number)

        if result.total_count > 0:
            glitch_count += result.total_count
            output.log(f"Glitch detected! Total: {glitch_count}")

    signal.signal(signal.SIGINT, signal_handler)

    # Get audio device
    output.console.print("\nSelect audio device")
    print_audio_devices()

    try:
        device_input = input("Device ID: ")
        device_id = int(device_input)
    except (ValueError, KeyboardInterrupt):
        output.log("Invalid device ID or cancelled", style="bold red")
        return

    # Start streaming
    try:
        with StreamReader(config, device_id) as stream:
            stream.save_blocks = save_blocks

            output.print_header("Audio Glitch Detector")
            output.reset_timer()

            # Start monitoring
            thread = stream.start_monitoring(glitch_callback, exit_event)

            # Start live output
            output.start_live_output(exit_event, lambda: stream.get_volume_db())
            output.log("Audio processing started")

            # Wait for completion
            thread.join()

            # Final summary
            output.stop_live_output()
            output.print_summary(glitch_count, output.get_elapsed_time())

    except Exception as e:
        output.log(f"Stream error: {e}", style="bold red")
        sys.exit(1)


def main() -> None:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()

    output = ConsoleOutput()

    if args.filename:
        run_file_mode(args.filename, args.threshold, args.block_size, args.save_blocks, output)
    else:
        config = AudioConfig(
            sample_rate=args.sample_rate,
            channels=args.channels,
            bit_depth=args.bit_depth,
            block_size=args.block_size,
        )

        try:
            config.validate()
        except ValueError as e:
            output.log(f"Invalid configuration: {e}", style="bold red")
            sys.exit(1)

        run_stream_mode(config, args.threshold, args.save_blocks, output)


if __name__ == "__main__":
    main()
