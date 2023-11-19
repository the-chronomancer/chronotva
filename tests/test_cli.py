import os
import sys
from pathlib import Path
from typing import Any, List
from unittest.mock import MagicMock, patch

import pytest

from src.chronotva.cli import main


@pytest.fixture
def temp_output_dir(tmp_path: Path) -> Path:
    output_dir: Path = tmp_path / "output"
    output_dir.mkdir()
    return output_dir


def run_cli_test(args: List[str], mock_plot: Any) -> None:
    with patch("src.chronotva.tesseract.BlockPlotter.plot_3d_blocks", mock_plot):
        with patch.object(sys, "argv", ["script_name"] + args):
            main()


def test_default_behavior(temp_output_dir: Path) -> None:
    test_args = [
        "--output-dir",
        str(temp_output_dir),
        "--pixel-width",
        "800",
        "--pixel-height",
        "600",
    ]
    mock_plot = MagicMock()
    run_cli_test(test_args, mock_plot)
    assert mock_plot.call_count == 261


def test_block_color_argument(temp_output_dir: Path) -> None:
    test_args = [
        "--block-color",
        "100,100,100,1",
        "--output-dir",
        str(temp_output_dir),
        "--pixel-width",
        "800",
        "--pixel-height",
        "600",
    ]
    mock_plot = MagicMock()
    run_cli_test(test_args, mock_plot)
    assert mock_plot.call_count == 261


def test_edge_color_argument(temp_output_dir: Path) -> None:
    test_args = [
        "--edge-color",
        "200,200,200,1",
        "--output-dir",
        str(temp_output_dir),
        "--pixel-width",
        "800",
        "--pixel-height",
        "600",
    ]
    mock_plot = MagicMock()
    run_cli_test(test_args, mock_plot)
    assert mock_plot.call_count == 261


def test_elevation_argument(temp_output_dir: Path) -> None:
    test_args = [
        "--elevation",
        "45",
        "--output-dir",
        str(temp_output_dir),
        "--pixel-width",
        "800",
        "--pixel-height",
        "600",
    ]
    mock_plot = MagicMock()
    run_cli_test(test_args, mock_plot)
    assert mock_plot.call_count == 261


def test_azimuth_argument(temp_output_dir: Path) -> None:
    test_args = [
        "--azimuth",
        "30",
        "--output-dir",
        str(temp_output_dir),
        "--pixel-width",
        "800",
        "--pixel-height",
        "600",
    ]
    mock_plot = MagicMock()
    run_cli_test(test_args, mock_plot)
    assert mock_plot.call_count == 261


def test_output_format_argument(temp_output_dir: Path) -> None:
    test_args = [
        "--output-format",
        "svg",
        "--output-dir",
        str(temp_output_dir),
        "--pixel-width",
        "800",
        "--pixel-height",
        "600",
    ]
    mock_plot = MagicMock()
    run_cli_test(test_args, mock_plot)
    assert mock_plot.call_count == 261


def test_dpi_argument(temp_output_dir: Path) -> None:
    test_args = [
        "--dpi",
        "200",
        "--output-dir",
        str(temp_output_dir),
        "--pixel-width",
        "800",
        "--pixel-height",
        "600",
    ]
    mock_plot = MagicMock()
    run_cli_test(test_args, mock_plot)
    assert mock_plot.call_count == 261


def test_transparent_argument(temp_output_dir: Path) -> None:
    test_args = [
        "--transparent",
        "--output-dir",
        str(temp_output_dir),
        "--pixel-width",
        "800",
        "--pixel-height",
        "600",
    ]
    mock_plot = MagicMock()
    run_cli_test(test_args, mock_plot)
    assert mock_plot.call_count == 261


def test_shade_argument(temp_output_dir: Path) -> None:
    test_args = [
        "--shade",
        "--output-dir",
        str(temp_output_dir),
        "--pixel-width",
        "800",
        "--pixel-height",
        "600",
    ]
    mock_plot = MagicMock()
    run_cli_test(test_args, mock_plot)
    assert mock_plot.call_count == 261


def test_show_axes_argument(temp_output_dir: Path) -> None:
    test_args = [
        "--show-axes",
        "--output-dir",
        str(temp_output_dir),
        "--pixel-width",
        "800",
        "--pixel-height",
        "600",
    ]
    mock_plot = MagicMock()
    run_cli_test(test_args, mock_plot)
    assert mock_plot.call_count == 261


def test_error_handling_pixel_dimensions_provided_separately(
    temp_output_dir: Path,
) -> None:
    test_args_width_only = [
        "--output-dir",
        str(temp_output_dir),
        "--pixel-width",
        "800",
    ]
    test_args_height_only = [
        "--output-dir",
        str(temp_output_dir),
        "--pixel-height",
        "600",
    ]
    with pytest.raises(SystemExit) as e:
        run_cli_test(test_args_width_only, MagicMock())
    assert e.type == SystemExit
    assert e.value.code == 2

    with pytest.raises(SystemExit) as e:
        run_cli_test(test_args_height_only, MagicMock())
    assert e.type == SystemExit
    assert e.value.code == 2


def test_error_handling_inch_width_provided_separately(
    temp_output_dir: Path,
) -> None:
    test_args_width_only = [
        "--output-dir",
        str(temp_output_dir),
        "--inch-width",
        "6.4",
    ]
    with pytest.raises(SystemExit) as e:
        run_cli_test(test_args_width_only, MagicMock())
    assert e.type == SystemExit
    assert e.value.code == 2


def test_error_handling_inch_height_provided_separately(
    temp_output_dir: Path,
) -> None:
    test_args_height_only = [
        "--output-dir",
        str(temp_output_dir),
        "--inch-height",
        "4.8",
    ]
    with pytest.raises(SystemExit) as e:
        run_cli_test(test_args_height_only, MagicMock())
    assert e.type == SystemExit
    assert e.value.code == 2


def test_combination_of_arguments(temp_output_dir: Path) -> None:
    test_args = [
        "--block-color",
        "100,100,100,1",
        "--edge-color",
        "200,200,200,1",
        "--elevation",
        "45",
        "--azimuth",
        "30",
        "--output-format",
        "svg",
        "--dpi",
        "200",
        "--transparent",
        "--shade",
        "--show-axes",
        "--output-dir",
        str(temp_output_dir),
        "--pixel-width",
        "800",
        "--pixel-height",
        "600",
    ]
    mock_plot = MagicMock()
    run_cli_test(test_args, mock_plot)
    assert mock_plot.call_count == 261


def test_error_handling_invalid_color_format(temp_output_dir: Path) -> None:
    test_args = [
        "--block-color",
        "invalid-color",
        "--output-dir",
        str(temp_output_dir),
        "--pixel-width",
        "800",
        "--pixel-height",
        "600",
    ]
    with pytest.raises(SystemExit) as e:
        run_cli_test(test_args, MagicMock())
    assert e.type == SystemExit
    assert e.value.code == 2


def test_error_handling_invalid_numeric_argument(temp_output_dir: Path) -> None:
    test_args = [
        "--elevation",
        "invalid",
        "--output-dir",
        str(temp_output_dir),
        "--pixel-width",
        "800",
        "--pixel-height",
        "600",
    ]
    with pytest.raises(SystemExit) as e:
        run_cli_test(test_args, MagicMock())
    assert e.type == SystemExit
    assert e.value.code == 2


def test_output_directory_creation() -> None:
    test_args = [
        "--output-dir",
        "non_existing_dir",
        "--pixel-width",
        "800",
        "--pixel-height",
        "600",
    ]
    mock_plot = MagicMock()
    run_cli_test(test_args, mock_plot)
    assert os.path.exists("non_existing_dir")
    os.rmdir("non_existing_dir")


def test_unfolding_ids_valid(temp_output_dir: Path) -> None:
    test_args = [
        "--unfolding-ids",
        "1,2,5",
        "--output-dir",
        str(temp_output_dir),
        "--pixel-width",
        "800",
        "--pixel-height",
        "600",
    ]
    mock_plot = MagicMock()
    run_cli_test(test_args, mock_plot)
    assert mock_plot.call_count == 3


def test_unfolding_ids_invalid_format(temp_output_dir: Path) -> None:
    test_args = [
        "--unfolding-ids",
        "abc,def",
        "--output-dir",
        str(temp_output_dir),
        "--pixel-width",
        "800",
        "--pixel-height",
        "600",
    ]
    with pytest.raises(SystemExit) as e:
        run_cli_test(test_args, MagicMock())
    assert e.type == SystemExit
    assert e.value.code == 2


def test_unfolding_ids_non_existent(temp_output_dir: Path) -> None:
    test_args = [
        "--unfolding-ids",
        "999",
        "--output-dir",
        str(temp_output_dir),
        "--pixel-width",
        "800",
        "--pixel-height",
        "600",
    ]
    mock_plot = MagicMock()
    run_cli_test(test_args, mock_plot)
    assert mock_plot.call_count == 0


def test_unfolding_ids_empty(temp_output_dir: Path) -> None:
    test_args = [
        "--output-dir",
        str(temp_output_dir),
        "--pixel-width",
        "800",
        "--pixel-height",
        "600",
    ]
    mock_plot = MagicMock()
    run_cli_test(test_args, mock_plot)
    expected_count = 261
    assert mock_plot.call_count == expected_count


if __name__ == "__main__":
    pytest.main()
