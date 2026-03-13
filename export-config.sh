#!/usr/bin/env bash
# Usage: bash export-config.sh [--data-dir PATH] > streamcontroller-config.nix
# Reads current StreamController pages and generates Nix Home Manager config.
# Requires: jq
set -euo pipefail

# --- Argument parsing ---
DATA_DIR=""
while [[ $# -gt 0 ]]; do
  case "$1" in
  --data-dir)
    DATA_DIR="$2"
    shift 2
    ;;
  -h | --help)
    echo "Usage: bash export-config.sh [--data-dir PATH] > streamcontroller-config.nix"
    echo ""
    echo "Reads current StreamController page JSON files and generates Nix"
    echo "Home Manager config for programs.streamcontroller."
    echo ""
    echo "Options:"
    echo "  --data-dir PATH  StreamController data directory"
    echo "                   Default: ~/.var/app/com.core447.StreamController/data (Flatpak)"
    echo "                   Fallback: ~/.local/share/StreamController (native)"
    exit 0
    ;;
  *)
    echo "Unknown argument: $1" >&2
    exit 1
    ;;
  esac
done

# --- Resolve data directory ---
if [[ -z $DATA_DIR ]]; then
  flatpak_dir="$HOME/.var/app/com.core447.StreamController/data"
  native_dir="${XDG_DATA_HOME:-$HOME/.local/share}/StreamController"
  if [[ -d "$flatpak_dir/pages" ]]; then
    DATA_DIR="$flatpak_dir"
  elif [[ -d "$native_dir/pages" ]]; then
    DATA_DIR="$native_dir"
  else
    echo "Error: Could not find StreamController data directory." >&2
    echo "Tried: $flatpak_dir" >&2
    echo "Tried: $native_dir" >&2
    echo "Use --data-dir to specify the path manually." >&2
    exit 1
  fi
fi

PAGES_DIR="$DATA_DIR/pages"
SETTINGS_DIR="$DATA_DIR/settings"

if [[ ! -d $PAGES_DIR ]]; then
  echo "Error: Pages directory not found: $PAGES_DIR" >&2
  exit 1
fi

if ! command -v jq &>/dev/null; then
  echo "Error: jq is required but not found in PATH." >&2
  exit 1
fi

# --- Helper: indent a string by N spaces ---
indent() {
  local n="$1"
  local prefix
  prefix=$(printf '%*s' "$n" '')
  sed "s/^/$prefix/"
}

# --- Helper: escape a string for Nix ---
nix_escape() {
  local s="$1"
  # Escape backslashes, then double quotes, then ${
  s="${s//\\/\\\\}"
  s="${s//\"/\\\"}"
  s="${s//\$/\\\$}"
  printf '%s' "$s"
}

# --- Helper: convert a JSON value to Nix literal ---
json_to_nix() {
  local json="$1"
  local indent_level="${2:-0}"
  local type
  type=$(echo "$json" | jq -r 'type')

  case "$type" in
  string)
    local val
    val=$(echo "$json" | jq -r '.')
    printf '"%s"' "$(nix_escape "$val")"
    ;;
  number)
    local val
    val=$(echo "$json" | jq -r '.')
    # Check if it's a float (has decimal point)
    if [[ $val == *.* ]]; then
      printf '%s' "$val"
    else
      printf '%s' "$val"
    fi
    ;;
  boolean)
    local val
    val=$(echo "$json" | jq -r '.')
    printf '%s' "$val"
    ;;
  null)
    printf 'null'
    ;;
  array)
    local len
    len=$(echo "$json" | jq 'length')
    if [[ $len -eq 0 ]]; then
      printf '[ ]'
      return
    fi
    local inner_indent=$((indent_level + 2))
    printf '[\n'
    local i
    for ((i = 0; i < len; i++)); do
      local elem
      elem=$(echo "$json" | jq ".[$i]")
      printf '%*s' "$inner_indent" ''
      json_to_nix "$elem" "$inner_indent"
      printf '\n'
    done
    printf '%*s]' "$indent_level" ''
    ;;
  object)
    local keys_len
    keys_len=$(echo "$json" | jq 'keys | length')
    if [[ $keys_len -eq 0 ]]; then
      printf '{ }'
      return
    fi
    local inner_indent=$((indent_level + 2))
    printf '{\n'
    local keys
    keys=$(echo "$json" | jq -r 'keys[]')
    while IFS= read -r key; do
      local val
      val=$(echo "$json" | jq ".[$(echo "$key" | jq -R .)]")
      printf '%*s' "$inner_indent" ''
      # Quote key if it contains special characters
      if [[ $key =~ ^[a-zA-Z_][a-zA-Z0-9_-]*$ ]] && [[ $key != *-* || $key =~ ^[a-zA-Z_][a-zA-Z0-9_-]*$ ]]; then
        printf '"%s"' "$key"
      else
        printf '"%s"' "$(nix_escape "$key")"
      fi
      printf ' = '
      json_to_nix "$val" "$inner_indent"
      printf ';\n'
    done <<<"$keys"
    printf '%*s}' "$indent_level" ''
    ;;
  esac
}

# --- Helper: emit a label position block ---
emit_label_pos() {
  local json="$1"
  local pos_name="$2"
  local indent_n="$3"
  local pad
  pad=$(printf '%*s' "$indent_n" '')

  # Check if this position exists and has any fields
  local pos_json
  pos_json=$(echo "$json" | jq ".\"$pos_name\" // empty" 2>/dev/null)
  if [[ -z $pos_json || $pos_json == "null" ]]; then
    return
  fi

  local has_content=false
  local text font_size color font_family font_weight outline_width
  text=$(echo "$pos_json" | jq -r '.text // empty')
  font_size=$(echo "$pos_json" | jq -r '."font-size" // empty')
  color=$(echo "$pos_json" | jq -r '.color // empty')
  font_family=$(echo "$pos_json" | jq -r '."font-family" // empty')
  font_weight=$(echo "$pos_json" | jq -r '."font-weight" // empty')
  outline_width=$(echo "$pos_json" | jq -r '.outline_width // empty')

  if [[ -n $text || -n $font_size || -n $color || -n $font_family || -n $font_weight || -n $outline_width ]]; then
    has_content=true
  fi

  if [[ $has_content == "false" ]]; then
    return
  fi

  echo "${pad}${pos_name} = {"
  local inner_pad
  inner_pad=$(printf '%*s' "$((indent_n + 2))" '')
  [[ -n $text ]] && echo "${inner_pad}text = \"$(nix_escape "$text")\";"
  [[ -n $font_size ]] && echo "${inner_pad}size = ${font_size};"
  [[ -n $color ]] && echo "${inner_pad}color = \"$(nix_escape "$color")\";"
  [[ -n $font_family ]] && echo "${inner_pad}font-family = \"$(nix_escape "$font_family")\";"
  [[ -n $font_weight ]] && echo "${inner_pad}font-weight = ${font_weight};"
  [[ -n $outline_width ]] && echo "${inner_pad}outline_width = ${outline_width};"
  echo "${pad}};"
}

# --- Helper: emit a state block ---
emit_state() {
  local state_json="$1"
  local state_id="$2"
  local indent_n="$3"
  local pad
  pad=$(printf '%*s' "$indent_n" '')
  local inner_pad
  inner_pad=$(printf '%*s' "$((indent_n + 2))" '')

  echo "${pad}\"${state_id}\" = {"

  # Labels
  local labels_json
  labels_json=$(echo "$state_json" | jq '.labels // empty' 2>/dev/null)
  if [[ -n $labels_json && $labels_json != "null" ]]; then
    local has_any_label=false
    for pos in top center bottom; do
      local pos_check
      pos_check=$(echo "$labels_json" | jq ".\"$pos\" // empty" 2>/dev/null)
      if [[ -n $pos_check && $pos_check != "null" ]]; then
        has_any_label=true
        break
      fi
    done
    if [[ $has_any_label == "true" ]]; then
      echo "${inner_pad}label = {"
      for pos in top center bottom; do
        emit_label_pos "$labels_json" "$pos" "$((indent_n + 4))"
      done
      echo "${inner_pad}};"
    fi
  fi

  # Media
  local media_json
  media_json=$(echo "$state_json" | jq '.media // empty' 2>/dev/null)
  if [[ -n $media_json && $media_json != "null" ]]; then
    local media_path media_size media_valign
    media_path=$(echo "$media_json" | jq -r '.path // empty')
    media_size=$(echo "$media_json" | jq -r '.size // empty')
    media_valign=$(echo "$media_json" | jq -r '.valign // empty')
    if [[ -n $media_path || -n $media_size || -n $media_valign ]]; then
      echo "${inner_pad}media = {"
      local media_inner_pad
      media_inner_pad=$(printf '%*s' "$((indent_n + 4))" '')
      [[ -n $media_path ]] && echo "${media_inner_pad}path = \"$(nix_escape "$media_path")\";"
      [[ -n $media_size ]] && echo "${media_inner_pad}size = ${media_size};"
      [[ -n $media_valign ]] && echo "${media_inner_pad}valign = \"$(nix_escape "$media_valign")\";"
      echo "${inner_pad}};"
    fi
  fi

  # Background color
  local bg_json
  bg_json=$(echo "$state_json" | jq -r '.background.color // empty' 2>/dev/null)
  if [[ -n $bg_json ]]; then
    echo "${inner_pad}background = \"$(nix_escape "$bg_json")\";"
  fi

  # Actions
  local actions_json
  actions_json=$(echo "$state_json" | jq '.actions // empty' 2>/dev/null)
  if [[ -n $actions_json && $actions_json != "null" ]]; then
    local actions_len
    actions_len=$(echo "$actions_json" | jq 'length')
    if [[ $actions_len -gt 0 ]]; then
      printf '%s' "${inner_pad}actions = "
      json_to_nix "$actions_json" "$((indent_n + 2))"
      printf ';\n'
    fi
  fi

  # image-control-action
  local ica
  ica=$(echo "$state_json" | jq '.["image-control-action"] // empty' 2>/dev/null)
  if [[ -n $ica && $ica != "null" && $ica != "0" ]]; then
    echo "${inner_pad}image-control-action = ${ica};"
  fi

  # label-control-actions
  local lca
  lca=$(echo "$state_json" | jq '.["label-control-actions"] // empty' 2>/dev/null)
  if [[ -n $lca && $lca != "null" ]]; then
    local lca_str
    lca_str=$(echo "$lca" | jq -c '.')
    # Only emit if not default [0,0,0]
    if [[ $lca_str != "[0,0,0]" ]]; then
      printf '%s' "${inner_pad}label-control-actions = "
      json_to_nix "$lca" "$((indent_n + 2))"
      printf ';\n'
    fi
  fi

  # background-control-action
  local bca
  bca=$(echo "$state_json" | jq '.["background-control-action"] // empty' 2>/dev/null)
  if [[ -n $bca && $bca != "null" && $bca != "0" ]]; then
    echo "${inner_pad}background-control-action = ${bca};"
  fi

  echo "${pad}};"
}

# --- Helper: emit a key block ---
emit_key() {
  local key_json="$1"
  local coord="$2"
  local indent_n="$3"
  local pad
  pad=$(printf '%*s' "$indent_n" '')

  echo "${pad}\"${coord}\" = {"
  echo "${pad}  states = {"

  local state_ids
  state_ids=$(echo "$key_json" | jq -r '.states | keys[]' 2>/dev/null)
  if [[ -n $state_ids ]]; then
    while IFS= read -r state_id; do
      local state_json
      state_json=$(echo "$key_json" | jq ".states[$(echo "$state_id" | jq -R .)]")
      emit_state "$state_json" "$state_id" "$((indent_n + 4))"
    done <<<"$state_ids"
  fi

  echo "${pad}  };"
  echo "${pad}};"
}

# --- Main output ---
echo "# Auto-generated StreamController config"
echo "# Source: $DATA_DIR"
echo "# Generated: $(date -Iseconds)"
echo ""
echo "programs.streamcontroller = {"
echo "  enable = true;"
echo ""

# --- Default pages ---
pages_settings="$SETTINGS_DIR/pages.json"
if [[ -f $pages_settings ]]; then
  default_pages=$(jq -r '.["default-pages"] // empty' "$pages_settings" 2>/dev/null)
  if [[ -n $default_pages && $default_pages != "null" ]]; then
    num_defaults=$(echo "$default_pages" | jq 'length')
    if [[ $num_defaults -gt 0 ]]; then
      echo "  defaultPages = {"
      echo "$default_pages" | jq -r 'to_entries[] | "    \"\(.key)\" = \"\(.value)\";"'
      echo "  };"
      echo ""
    fi
  fi
fi

# --- Pages ---
page_files=()
for f in "$PAGES_DIR"/*.json; do
  [[ -f $f ]] && page_files+=("$f")
done

if [[ ${#page_files[@]} -gt 0 ]]; then
  echo "  pages = {"
  for page_file in "${page_files[@]}"; do
    page_name=$(basename "$page_file" .json)
    page_json=$(jq '.' "$page_file")

    echo ""
    echo "    \"${page_name}\" = {"

    # Brightness
    brightness_json=$(echo "$page_json" | jq '.brightness // empty' 2>/dev/null)
    if [[ -n $brightness_json && $brightness_json != "null" ]]; then
      brightness_val=$(echo "$brightness_json" | jq -r '.value // empty')
      brightness_ow=$(echo "$brightness_json" | jq -r '.overwrite // empty')
      if [[ -n $brightness_val || -n $brightness_ow ]]; then
        echo "      brightness = {"
        [[ -n $brightness_val ]] && echo "        value = ${brightness_val};"
        [[ -n $brightness_ow && $brightness_ow != "false" ]] && echo "        overwrite = ${brightness_ow};"
        echo "      };"
      fi
    fi

    # Screensaver
    screensaver_json=$(echo "$page_json" | jq '.screensaver // empty' 2>/dev/null)
    if [[ -n $screensaver_json && $screensaver_json != "null" ]]; then
      printf '      screensaver = '
      json_to_nix "$screensaver_json" 6
      printf ';\n'
    fi

    # Extra config — everything that's not keys, brightness, screensaver
    extra_json=$(echo "$page_json" | jq 'del(.keys, .brightness, .screensaver) | if . == {} then empty else . end' 2>/dev/null)
    if [[ -n $extra_json && $extra_json != "null" ]]; then
      printf '      extraConfig = '
      json_to_nix "$extra_json" 6
      printf ';\n'
    fi

    # Keys
    keys_json=$(echo "$page_json" | jq '.keys // empty' 2>/dev/null)
    if [[ -n $keys_json && $keys_json != "null" ]]; then
      key_count=$(echo "$keys_json" | jq 'length')
      if [[ $key_count -gt 0 ]]; then
        echo "      keys = {"
        key_coords=$(echo "$keys_json" | jq -r 'keys[]')
        while IFS= read -r coord; do
          key_json=$(echo "$keys_json" | jq ".[$(echo "$coord" | jq -R .)]")
          emit_key "$key_json" "$coord" 8
        done <<<"$key_coords"
        echo "      };"
      fi
    fi

    echo "    };"
  done
  echo ""
  echo "  };"
fi

echo "};"
