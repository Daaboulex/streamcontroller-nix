"""Button/key management — set images, labels, actions on page keys."""

import os
from typing import Optional

from cli_anything.streamcontroller.core.settings import load_json, save_json


class ButtonManager:
    """Manages individual button/key configuration within pages."""

    def __init__(self, data_path: str):
        self.data_path = data_path
        self.pages_dir = os.path.join(data_path, "pages")

    def _resolve_page_path(self, page_name: str) -> str:
        """Resolve page name to path."""
        if os.path.isfile(page_name):
            return page_name
        path = os.path.join(self.pages_dir, f"{page_name}.json")
        if os.path.isfile(path):
            return path
        # Case-insensitive fallback
        target = page_name.lower()
        for f in os.listdir(self.pages_dir):
            if f.endswith(".json") and os.path.splitext(f)[0].lower() == target:
                return os.path.join(self.pages_dir, f)
        raise FileNotFoundError(f"Page '{page_name}' not found")

    def _parse_coord(self, coord: str) -> str:
        """Normalize coordinate format to 'CxR' (e.g., '0x0', '2x1').

        Accepts: '0x0', '0,0', '(0,0)'
        """
        coord = coord.strip().strip("()")
        if "," in coord:
            parts = coord.split(",")
            return f"{parts[0].strip()}x{parts[1].strip()}"
        return coord

    # --- Get/Set key data ---

    def get_key(self, page_name: str, coord: str, input_type: str = "keys") -> dict:
        """Get key data at a coordinate."""
        path = self._resolve_page_path(page_name)
        data = load_json(path)
        coord = self._parse_coord(coord)
        return data.get(input_type, {}).get(coord, {})

    def get_key_state(self, page_name: str, coord: str, state: int = 0, input_type: str = "keys") -> dict:
        """Get state data for a key."""
        key = self.get_key(page_name, coord, input_type)
        return key.get("states", {}).get(str(state), {})

    def set_key_state(self, page_name: str, coord: str, state: int, state_data: dict, input_type: str = "keys"):
        """Set state data for a key."""
        path = self._resolve_page_path(page_name)
        data = load_json(path)
        coord = self._parse_coord(coord)
        data.setdefault(input_type, {}).setdefault(coord, {}).setdefault("states", {})[str(state)] = state_data
        save_json(path, data)

    # --- Labels ---

    def get_labels(self, page_name: str, coord: str, state: int = 0) -> dict:
        """Get all labels for a key state."""
        state_data = self.get_key_state(page_name, coord, state)
        return state_data.get("labels", {})

    def set_label(self, page_name: str, coord: str, position: str, text: str,
                  state: int = 0, font_family: str = None, font_size: int = None,
                  color: list = None):
        """Set a label on a key.

        Args:
            position: 'top', 'center', or 'bottom'
        """
        path = self._resolve_page_path(page_name)
        data = load_json(path)
        coord_key = self._parse_coord(coord)

        states = data.setdefault("keys", {}).setdefault(coord_key, {}).setdefault("states", {})
        state_data = states.setdefault(str(state), {})
        labels = state_data.setdefault("labels", {})
        label = labels.setdefault(position, {})

        label["text"] = text
        if font_family is not None:
            label["font-family"] = font_family
        if font_size is not None:
            label["font-size"] = font_size
        if color is not None:
            label["color"] = color

        save_json(path, data)

    def clear_label(self, page_name: str, coord: str, position: str, state: int = 0):
        """Clear a label from a key."""
        path = self._resolve_page_path(page_name)
        data = load_json(path)
        coord_key = self._parse_coord(coord)

        labels = (data.get("keys", {}).get(coord_key, {})
                  .get("states", {}).get(str(state), {})
                  .get("labels", {}))
        if position in labels:
            del labels[position]
            save_json(path, data)

    # --- Media / Images ---

    def get_image(self, page_name: str, coord: str, state: int = 0) -> Optional[str]:
        """Get the image path for a key state."""
        state_data = self.get_key_state(page_name, coord, state)
        return state_data.get("media", {}).get("path")

    def set_image(self, page_name: str, coord: str, image_path: str, state: int = 0):
        """Set the image for a key state."""
        path = self._resolve_page_path(page_name)
        image_path = os.path.expanduser(image_path)
        if not os.path.isfile(image_path):
            raise FileNotFoundError(f"Image file '{image_path}' not found")
        image_path = os.path.abspath(image_path)

        data = load_json(path)
        coord_key = self._parse_coord(coord)
        states = data.setdefault("keys", {}).setdefault(coord_key, {}).setdefault("states", {})
        state_data = states.setdefault(str(state), {})
        media = state_data.setdefault("media", {})
        media["path"] = image_path
        save_json(path, data)

    def clear_image(self, page_name: str, coord: str, state: int = 0):
        """Clear the image from a key state."""
        path = self._resolve_page_path(page_name)
        data = load_json(path)
        coord_key = self._parse_coord(coord)

        media = (data.get("keys", {}).get(coord_key, {})
                 .get("states", {}).get(str(state), {})
                 .get("media", {}))
        if "path" in media:
            media["path"] = None
            save_json(path, data)

    # --- Actions ---

    def get_actions(self, page_name: str, coord: str, state: int = 0) -> list:
        """Get actions for a key state."""
        state_data = self.get_key_state(page_name, coord, state)
        return state_data.get("actions", [])

    def set_action(self, page_name: str, coord: str, action_id: str,
                   state: int = 0, settings: dict = None):
        """Set (replace) the action on a key state."""
        path = self._resolve_page_path(page_name)
        data = load_json(path)
        coord_key = self._parse_coord(coord)

        states = data.setdefault("keys", {}).setdefault(coord_key, {}).setdefault("states", {})
        state_data = states.setdefault(str(state), {})
        action = {"id": action_id}
        if settings:
            action["settings"] = settings
        state_data["actions"] = [action]
        save_json(path, data)

    def add_action(self, page_name: str, coord: str, action_id: str,
                   state: int = 0, settings: dict = None):
        """Add an action to a key state (appends to existing actions)."""
        path = self._resolve_page_path(page_name)
        data = load_json(path)
        coord_key = self._parse_coord(coord)

        states = data.setdefault("keys", {}).setdefault(coord_key, {}).setdefault("states", {})
        state_data = states.setdefault(str(state), {})
        actions = state_data.setdefault("actions", [])
        action = {"id": action_id}
        if settings:
            action["settings"] = settings
        actions.append(action)
        save_json(path, data)

    def clear_actions(self, page_name: str, coord: str, state: int = 0):
        """Remove all actions from a key state."""
        path = self._resolve_page_path(page_name)
        data = load_json(path)
        coord_key = self._parse_coord(coord)

        state_data = (data.get("keys", {}).get(coord_key, {})
                      .get("states", {}).get(str(state), {}))
        if "actions" in state_data:
            state_data["actions"] = []
            save_json(path, data)

    # --- List all configured keys ---

    def list_keys(self, page_name: str) -> list:
        """List all configured keys on a page with summary info."""
        path = self._resolve_page_path(page_name)
        data = load_json(path)
        keys = []
        for input_type in ["keys", "dials", "touchscreens"]:
            for coord, key_data in data.get(input_type, {}).items():
                states = key_data.get("states", {})
                n_states = len(states)
                # Get info from state 0
                state0 = states.get("0", {})
                labels = state0.get("labels", {})
                media = state0.get("media", {})
                actions = state0.get("actions", [])
                label_text = ""
                for pos in ["center", "bottom", "top"]:
                    t = labels.get(pos, {}).get("text", "")
                    if t:
                        label_text = t
                        break
                keys.append({
                    "type": input_type,
                    "coordinate": coord,
                    "states": n_states,
                    "label": label_text,
                    "image": media.get("path"),
                    "actions": [a.get("id", "") for a in actions] if isinstance(actions, list) else [],
                })
        return keys
