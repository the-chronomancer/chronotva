import logging
from typing import List, NamedTuple, Optional, Tuple, cast

import matplotlib.pyplot as plt  # type: ignore
from matplotlib.colors import to_rgba  # type: ignore
from mpl_toolkits.mplot3d import Axes3D  # type: ignore

logger = logging.getLogger(__name__)


class PlotParameters(NamedTuple):
    """Container for plot parameters.

    Attributes:
        colors: A list of RGBA color tuples for the blocks.
        edgecolors: A list of RGBA color tuples for the edges of the blocks.
        view_angle: A tuple containing the elevation and azimuth angles for the 3D plot.
        dpi: Dots per inch for the output image.
        transparent: Whether the output image should have a transparent background.
        shade: Whether to enable shading in the 3D plot.
        show_axes: Whether to show axes in the plot.
        bbox_inches: To use 'tight' and remove whitespace or not.
        height: Height of the output image in inches.
        width: Width of the output image in inches.
    """

    colors: List[Tuple[float, float, float, float]]
    edgecolors: List[Tuple[float, float, float, float]]
    view_angle: Tuple[float, float]
    dpi: int
    transparent: bool
    shade: bool
    show_axes: bool
    bbox_inches: Optional[str]
    height: float
    width: float


def parse_rgba_list(color_string: str) -> List[Tuple[float, float, float, float]]:
    """Parses a string of color values into a list of RGBA tuples.

    Args:
        color_string: A string containing color values separated by semicolons.

    Returns:
        A list of RGBA color tuples.

    Raises:
        ValueError: If an RGBA tuple does not have exactly 4 elements or if an invalid color is provided.
    """
    rgba_list = []

    for color in color_string.split(";"):
        try:
            rgba = (
                tuple(
                    float(c) / 255 if i < 3 else float(c)
                    for i, c in enumerate(color.split(","))
                )
                if "," in color
                else to_rgba(color)  # type: ignore
            )
            if len(rgba) != 4:
                raise ValueError("RGBA tuple must have exactly 4 elements.")
        except ValueError as error:
            raise ValueError(f"Invalid color value: {color}. Error: {error}")

        rgba_list.append(rgba)

    return rgba_list


class BlockPlotter:
    """
    A class for plotting 3D blocks based on provided coordinates.
    """

    def __init__(
        self,
    ) -> None:
        pass

    def plot_3d_blocks(
        self,
        coordinates: List[Tuple[int, int, int]],
        plot_params: PlotParameters,
        output_format: str,
        output_path: str,
    ) -> None:
        """Plots 3D blocks using the provided coordinates and plot parameters.

        Args:
            coordinates: A list of tuples representing the (x, y, z) coordinates of the blocks.
            plot_params: A PlotParameters object containing the plot configuration.
            output_format: The file format for the output image (e.g., 'png', 'svg', 'pdf').
            output_path: The file path where the output image will be saved.

        Raises:
            TypeError: If coordinates are not provided as a list of tuples.
            ValueError: If no coordinates are provided for plotting.
            Exception: If an error occurs during plotting.
        """
        if not isinstance(coordinates, List):
            raise TypeError("Coordinates must be a list of tuples.")

        if not coordinates:
            raise ValueError("No coordinates provided for plotting.")

        try:
            fig = plt.figure(figsize=(plot_params.width, plot_params.height))
            axes: Axes3D = cast(Axes3D, fig.add_subplot(111, projection="3d"))

            for i, (x, y, z) in enumerate(coordinates):
                color = plot_params.colors[i % len(plot_params.colors)]
                edgecolor = plot_params.edgecolors[i % len(plot_params.edgecolors)]

                axes.bar3d(
                    x,
                    y,
                    z,
                    dx=1,
                    dy=1,
                    dz=1,
                    color=color,
                    edgecolor=edgecolor,
                    shade=plot_params.shade,
                )

            if not plot_params.show_axes:
                axes.axis("off")

            axes.set_box_aspect(
                [
                    upper - lower
                    for lower, upper in (
                        getattr(axes, f"get_{dim}lim")() for dim in "xyz"
                    )
                ]
            )

            axes.view_init(*plot_params.view_angle)

            plt.tight_layout()
            plt.savefig(
                output_path,
                bbox_inches=plot_params.bbox_inches,
                pad_inches=0,
                dpi=plot_params.dpi,
                transparent=plot_params.transparent,
                format=output_format,
            )

            plt.close(fig)

        except Exception as error:
            logging.error(f"An error occurred while plotting: {error}")
            raise
