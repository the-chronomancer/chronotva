import argparse
import datetime
import logging
import os
import sys
from typing import Dict, List, Optional, Tuple

from .default_data import default_data as data
from .tesseract import BlockPlotter, PlotParameters, parse_rgba_list

logger = logging.getLogger(__name__)


def parse_arguments(args: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse command-line arguments for chronotva.

    Args:
        args: A list of strings representing the command-line arguments. If None,
              the default sys.argv will be parsed.

    Returns:
        An argparse.Namespace object containing the parsed arguments.
    """
    parser = argparse.ArgumentParser(description="ChronoTVA")
    parser.add_argument(
        "-b",
        "--block-color",
        type=str,
        default="230,230,230,1",
        help="Block color in RGBA format or color name. Multiple colors can be separated by semicolons. Default: '230,230,230,1'",
    )
    parser.add_argument(
        "-e",
        "--edge-color",
        type=str,
        default="25,25,25,1",
        help="Block edge color in RGBA format or color name. Multiple colors can be separated by semicolons. Default: '25,25,25,1'",
    )
    parser.add_argument(
        "-v",
        "--elevation",
        type=float,
        default=30,
        help="Elevation angle for the plot in degrees. Default: 30",
    )
    parser.add_argument(
        "-a",
        "--azimuth",
        type=float,
        default=22.5,
        help="Azimuth angle for the plot in degrees. Default: 22.5",
    )
    parser.add_argument(
        "-f",
        "--output-format",
        type=str,
        default="svg",
        choices=["png", "svg", "pdf"],
        help="Output file format. Options: png, svg, pdf. Default: 'svg'",
    )
    parser.add_argument(
        "-d",
        "--output-dir",
        type=str,
        help="Output directory for the plots. If not specified, a default directory will be created.",
    )
    parser.add_argument(
        "-p",
        "--dpi",
        type=int,
        default=300,
        help="DPI (dots per inch) for the output image. Default: 300",
    )
    parser.add_argument(
        "-t",
        "--transparent",
        action="store_true",
        default=True,
        help="Enable transparency in the output image. Default: True",
    )
    parser.add_argument(
        "-s",
        "--shade",
        action="store_true",
        default=False,
        help="Enable shading in the 3D plot. Default: False",
    )
    parser.add_argument(
        "-x",
        "--show-axes",
        action="store_true",
        help="Show axes in the plot. Default: False",
    )
    parser.add_argument(
        "-u",
        "--unfolding-ids",
        type=parse_unfolding_ids,
        help="Comma-separated numeric identifiers of unfoldings to plot, e.g., '1,2,5'. If not provided, all unfoldings will be processed.",
        default=None,
    )
    parser.add_argument(
        "-w",
        "--whitespace-removal",
        action="store_true",
        default=True,
        help="Remove whitespace around the image. Default behavior is to remove whitespace.",
    )
    parser.add_argument(
        "--pixel-height", type=int, help="Height of the output image in pixels."
    )
    parser.add_argument(
        "--pixel-width", type=int, help="Width of the output image in pixels."
    )
    parser.add_argument(
        "--inch-height",
        type=float,
        default=6.4,
        help="Height of the output image in inches.",
    )
    parser.add_argument(
        "--inch-width",
        type=float,
        default=4.8,
        help="Width of the output image in inches.",
    )
    return parser.parse_args(args)


def parse_unfolding_ids(value: str) -> List[int]:
    """Parse a string of comma-separated unfolding IDs into a list of integers.

    Args:
        value: A string containing comma-separated numeric identifiers.

    Returns:
        A list of integers representing the unfolding IDs.

    Raises:
        argparse.ArgumentTypeError: If the input string cannot be parsed into integers.
    """
    try:
        return [int(item) for item in value.split(",")]
    except ValueError:
        raise argparse.ArgumentTypeError(
            "Unfolding IDs must be a comma-separated list of integers."
        )


def build_configuration(args: argparse.Namespace) -> PlotParameters:
    """Build the plot configuration from the parsed arguments.

    Args:
        args: An argparse.Namespace object containing the parsed command-line arguments.

    Returns:
        A PlotParameters object with the configuration for plotting.

    Raises:
        ValueError: If there are inconsistencies in the provided arguments.
    """
    if (args.pixel_width is not None and args.pixel_height is None) or (
        args.pixel_width is None and args.pixel_height is not None
    ):
        raise ValueError(
            "Both --pixel-width and --pixel-height must be provided together if one is provided."
        )

    if args.inch_width != 6.4 or args.inch_height != 4.8:
        user_provided_inch_dimensions = True
    else:
        user_provided_inch_dimensions = False

    if user_provided_inch_dimensions and (
        args.inch_width == 6.4 or args.inch_height == 4.8
    ):
        raise ValueError(
            "Both --inch-width and --inch-height must be provided together if one is provided."
        )

    if args.pixel_width is not None and args.pixel_height is not None:
        width = args.pixel_width / args.dpi
        height = args.pixel_height / args.dpi
    else:
        width = args.inch_width
        height = args.inch_height

    if args.whitespace_removal == True:
        bbox_inches = "tight"
    else:
        bbox_inches = args.whitespace_removal

    block_colors = parse_rgba_list(args.block_color)
    edge_colors = parse_rgba_list(args.edge_color)
    view_angle = (args.elevation, args.azimuth)

    plot_params = PlotParameters(
        colors=block_colors,
        edgecolors=edge_colors,
        view_angle=view_angle,
        dpi=args.dpi,
        transparent=args.transparent,
        shade=args.shade,
        show_axes=args.show_axes,
        bbox_inches=bbox_inches,
        height=height,
        width=width,
    )

    return plot_params


def prepare_output_directory(args: argparse.Namespace) -> str:
    """Prepare the output directory for saving plots.

    Args:
        args: An argparse.Namespace object containing the parsed command-line arguments.

    Returns:
        The path to the output directory.
    """
    output_folder = args.output_dir or datetime.datetime.now().strftime(
        "output/%Y%m%d_%H%M%S"
    )
    os.makedirs(output_folder, exist_ok=True)
    return output_folder


def perform_plotting(
    plot_params: PlotParameters,
    data: Dict[int, List[Tuple[int, int, int]]],
    output_folder: str,
    output_format: str,
    unfolding_ids: Optional[List[int]] = None,
) -> None:
    """Perform the plotting of 3D blocks based on the provided data and parameters.

    Args:
        plot_params: A PlotParameters object containing the plot configuration.
        data: A dictionary mapping unfolding IDs to lists of block coordinates.
        output_folder: The path to the directory where output images will be saved.
        output_format: The file format for the output images.
        unfolding_ids: An optional list of unfolding IDs to plot. If None, all unfoldings will be plotted.
    """
    plotter = BlockPlotter()
    if unfolding_ids is not None:
        filtered_data = {uid: data[uid] for uid in unfolding_ids if uid in data}
    else:
        filtered_data = data
    for unfolding_id, coordinates in filtered_data.items():
        output_filename = f"unfolding_{unfolding_id}.{output_format}"
        output_path = os.path.join(output_folder, output_filename)
        plotter.plot_3d_blocks(coordinates, plot_params, output_format, output_path)
        logger.info(f"Saved '{output_path}'")
    if unfolding_ids:
        logger.info(
            f"Plotted unfoldings with IDs: {', '.join(map(str, unfolding_ids))}"
        )
    else:
        logger.info("All requested unfolding images have been generated and saved!")


def main() -> None:
    """The main function for ChronoTVA."""
    try:
        args = parse_arguments()
        plot_params = build_configuration(args)
        output_folder = prepare_output_directory(args)
        perform_plotting(
            plot_params, data, output_folder, args.output_format, args.unfolding_ids
        )
    except ValueError as e:
        logger.error(f"Configuration Error: {e}")
        sys.exit(2)
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
