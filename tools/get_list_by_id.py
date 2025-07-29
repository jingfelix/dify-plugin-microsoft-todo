import logging
from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities import I18nObject, ParameterOption
from dify_plugin.entities.tool import ToolInvokeMessage

from src.mstodo import *

logger = logging.getLogger(__name__)


class DifyPluginPdmTemplateTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, Any, Any]:

        plugin = MSTodoPlugin(credentials=MSTodoCredentials(**self.runtime.credentials))

        for res in plugin.get_list_by_id(**tool_parameters):
            if isinstance(res, str):
                yield self.create_text_message(res)
            elif isinstance(res, list):
                yield self.create_json_message(
                    {
                        "data": res,
                    }
                )
            elif isinstance(res, dict):
                yield self.create_json_message(res)
            else:
                yield self.create_text_message(str(res))

    def _fetch_parameter_options(self, parameter: str) -> list[ParameterOption]:

        logger.debug(f"Fetching parameter options for: {parameter}")

        match parameter:
            case "list_id":
                token: Token = Token(**json.loads(self.runtime.credentials["token"]))
                if not token:
                    raise ValueError("Token is required to invoke this tool.")

                todo_client = ToDoConnection(
                    client_id="",
                    client_secret="",
                    token=token,
                )

                return [
                    ParameterOption(
                        value=task_list.list_id,
                        label=I18nObject(en_US=task_list.displayName),
                    )
                    for task_list in todo_client.get_lists()
                ]
            case _:
                logger.error(f"Unsupported parameter: {parameter}")
                raise NotImplementedError(
                    "Unsupported parameter" f"{parameter} for this tool."
                )
