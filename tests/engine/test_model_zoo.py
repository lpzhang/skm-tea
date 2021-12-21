import os
import pathlib
import re
from typing import Any, Dict

import torch.nn as nn

import skm_tea as st

from .. import util

REPO_DIR = pathlib.Path(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
LOCAL_MODEL_ZOO_FILE = REPO_DIR / "MODEL_ZOO.md"


def test_build_deployment_model():
    model = st.get_model_from_zoo(
        cfg_or_file="download://https://drive.google.com/file/d/1BJc_lidyHyZvkFD4pLDfSH2Gp2gWXPww/view?usp=sharing",  # noqa: E501
        weights_path="download://https://drive.google.com/file/d/1EkSdXtnD_28_pjZeVFD6XtYugU7VM3jo/view?usp=sharing",  # noqa: E501
        force_download=True,
    )
    assert isinstance(model, nn.Module)


def test_model_zoo_configs():
    """
    Test that all models in the zoo can be built with the appropriate config
    and weight files.

    Note:
        This function does not test if the config can be used for training.
        For now, the user must validate this manually.
    """
    models = _parse_model_zoo()
    for name, model_info in models.items():
        try:
            model = st.get_model_from_zoo(
                f"download://{model_info['cfg_url']}",
                f"download://{model_info['weights_url']}",
                force_download=True,
            )
            assert isinstance(model, nn.Module)
        except Exception as e:
            raise type(e)(f"Failed to build model {name}:\n{e}")


def _parse_model_zoo() -> Dict[str, Dict[str, Any]]:
    """Returns a dictionary representation of the model zoo.

    This function parses the MODEL_ZOO.md file and returns a dictionary
    mapping from the model name to the diction of model information.
    """

    def _has_model_line(line):
        return re.match("^\|.*\[cfg\].*$", line) is not None

    def _parse_model_line(line):
        columns = line.split("|")[1:]
        return {
            "name": columns[0].strip(),
            "cfg_url": re.search("\[cfg\]\((.+?)\)", line).group(1),
            "weights_url": re.search("\[model\]\((.+?)\)", line).group(1),
        }

    with open(LOCAL_MODEL_ZOO_FILE) as f:
        lines = f.readlines()
    lines = [line.strip() for line in lines]
    lines = [line for line in lines if line]
    node, _ = util.parse_markdown(lines)

    models = {}
    for heading, content in node.to_dict(flatten=True).items():
        if not content or not any(_has_model_line(line) for line in content):
            continue
        model_content = [line for line in content if _has_model_line(line)]

        for model_line in model_content:
            model_data = _parse_model_line(model_line)
            models[f"{heading}/{model_data['name']}"] = model_data
    return models
