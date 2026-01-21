#
# Copyright 2023 ABSA Group Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""Main entrypoint for the Living Doc Generator PDF GitHub Action.

This is a temporary migrated entrypoint: it wires logging + inputs and delegates
to :class:`generator.generator.PdfGenerator`.
"""

import logging

from generator.action_inputs import ActionInputs
from generator.generator import PdfGenerator
from generator.utils.gh_action import set_action_failed, set_action_output
from generator.utils.logging_config import setup_logging


def run() -> None:
    """
    Run the Living Doc Generator PDF action.

    @return: None
    """
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Starting 'Living Doc Generator PDF' GitHub Action")

    ActionInputs.validate_inputs()

    try:
        generator = PdfGenerator()
        pdf_path = generator.generate()
    except Exception as exc:  # pylint: disable=broad-except
        set_action_failed(f"Failed to generate PDF. Error: {exc}")
        return

    if not pdf_path:
        set_action_failed("Failed to generate PDF. See logs for details.")
        return

    set_action_output("pdf-path", pdf_path)
    logger.info("GitHub Action 'Living Doc Generator PDF' completed successfully")


if __name__ == "__main__":
    run()
