import html as html_lib


ICONS: dict[str, str] = {
    "student": "school",
    "teacher": "badge",
    "face_id": "face",
    "lock": "lock",
    "login": "login",
    "logout": "logout",
    "register": "person_add",
    "back": "arrow_back",
    "arrow_outward": "arrow_outward",
    "camera": "photo_camera",
    "upload": "upload_file",
    "photos": "photo_prints",
    "mic": "mic",
    "attendance": "fact_check",
    "subjects": "menu_book",
    "records": "analytics",
    "students_count": "group",
    "classes_count": "schedule",
    "total_classes": "calendar_month",
    "attended": "check_circle",
    "absent": "cancel",
    "share": "share",
    "add": "add",
    "delete": "delete",
    "unenroll": "delete_forever",
    "done": "check",
    "close": "close",
    "warning": "warning",
    "error": "error",
    "info": "info",
    "welcome": "waving_hand",
    "link": "link",
    "qr_code": "qr_code_2",
}


def st_icon(key: str) -> str:
    """Return a Streamlit Material Symbols shortcode for native widget icons."""
    icon_name = ICONS[key]
    return f":material/{icon_name}:"


def html_icon(
    key: str,
    size: str = "sm",
    color: str | None = None,
    extra_class: str = "",
) -> str:
    """Render a reusable Material Symbols outline icon span for HTML/markdown UI."""
    icon_name = html_lib.escape(ICONS[key])
    size_class = f"sc-icon-{size}" if size in {"sm", "md", "lg"} else "sc-icon-sm"
    classes = f"sc-icon {size_class} {extra_class}".strip()
    style_attr = f' style="color:{html_lib.escape(color)};"' if color else ""
    return (
        f'<span class="{classes}" aria-hidden="true" translate="no"{style_attr}>'
        f"{icon_name}</span>"
    )

