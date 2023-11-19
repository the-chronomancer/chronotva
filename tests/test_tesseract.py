import os
from pathlib import Path
from typing import cast
from unittest.mock import MagicMock, Mock, patch

import pytest
from matplotlib.colors import to_rgba  # type: ignore

from src.chronotva.tesseract import BlockPlotter, PlotParameters, parse_rgba_list


@pytest.fixture
def temp_output_dir(tmp_path: Path) -> Path:
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    return output_dir


def test_parse_rgba_list() -> None:
    color_string = "230,230,230,1;25,25,25,1"
    rgba_list = parse_rgba_list(color_string)
    assert rgba_list == [
        (230 / 255, 230 / 255, 230 / 255, 1),
        (25 / 255, 25 / 255, 25 / 255, 1),
    ]


def test_parse_rgba_list_named_colors() -> None:
    color_string = "red;blue;green"
    rgba_list = parse_rgba_list(color_string)
    assert rgba_list == [to_rgba("red"), to_rgba("blue"), to_rgba("green")]  # type: ignore


def test_parse_rgba_list_invalid_colors() -> None:
    color_string = "invalid;color;string"
    with pytest.raises(ValueError):
        parse_rgba_list(color_string)


class TestBlockPlotter:
    @pytest.fixture
    def plotter(self) -> BlockPlotter:
        return BlockPlotter()

    @pytest.fixture
    def plot_params(self) -> PlotParameters:
        return PlotParameters(
            colors=[(1, 0, 0, 1)],
            edgecolors=[(0, 0, 0, 1)],
            view_angle=(30, 22.5),
            dpi=300,
            transparent=False,
            shade=False,
            show_axes=True,
            bbox_inches="tight",
            height=4.8,
            width=6.4,
        )

    @patch("matplotlib.pyplot.savefig")
    def test_plot_3d_blocks_valid(
        self,
        mock_savefig: MagicMock,
        plotter: BlockPlotter,
        plot_params: PlotParameters,
        temp_output_dir: Path,
    ) -> None:
        coordinates = [(1, 2, 3)]
        plotter.plot_3d_blocks(
            coordinates, plot_params, "png", str(temp_output_dir / "output.png")
        )
        mock_savefig.assert_called_once()

    @pytest.mark.parametrize(
        "transparent, shade, show_axes", [(True, True, True), (False, False, False)]
    )
    def test_plot_3d_blocks_different_params(
        self,
        plotter: BlockPlotter,
        plot_params: PlotParameters,
        temp_output_dir: Path,
        transparent: bool,
        shade: bool,
        show_axes: bool,
    ) -> None:
        updated_params = plot_params._replace(
            transparent=transparent, shade=shade, show_axes=show_axes
        )
        coordinates = [(1, 2, 3)]
        output_path = str(temp_output_dir / "diff_params_output.png")
        plotter.plot_3d_blocks(coordinates, updated_params, "png", output_path)
        assert os.path.exists(output_path) and os.path.getsize(output_path) > 0

    def test_plot_3d_blocks_invalid_input(
        self, plotter: BlockPlotter, plot_params: PlotParameters
    ) -> None:
        invalid_coordinates = cast(list[tuple[int, int, int]], "invalid_input")
        with pytest.raises(TypeError):
            plotter.plot_3d_blocks(
                invalid_coordinates, plot_params, "png", "output.png"
            )

    @patch("builtins.open", side_effect=PermissionError)
    def test_permission_error_handling(
        self,
        mock_open: Mock,
        plotter: BlockPlotter,
        plot_params: PlotParameters,
        temp_output_dir: Path,
    ) -> None:
        coordinates = [(1, 2, 3)]
        try:
            plotter.plot_3d_blocks(
                coordinates,
                plot_params,
                "png",
                str(temp_output_dir / "error_output.png"),
            )
            assert False, "PermissionError was not raised as expected"
        except PermissionError:
            pass

    def test_plot_3d_blocks_empty_coordinates(
        self, plotter: BlockPlotter, plot_params: PlotParameters, temp_output_dir: Path
    ) -> None:
        with pytest.raises(ValueError):
            plotter.plot_3d_blocks(
                [], plot_params, "png", str(temp_output_dir / "output.png")
            )

    @patch("matplotlib.pyplot.savefig")
    def test_plot_3d_blocks_single_color(
        self,
        mock_savefig: MagicMock,
        plotter: BlockPlotter,
        plot_params: PlotParameters,
        temp_output_dir: Path,
    ) -> None:
        coordinates = [(1, 2, 3), (4, 5, 6)]
        plot_params = plot_params._replace(
            colors=[(1, 0, 0, 1)], edgecolors=[(0, 0, 0, 1)]
        )
        plotter.plot_3d_blocks(
            coordinates, plot_params, "png", str(temp_output_dir / "output.png")
        )
        mock_savefig.assert_called_once()
