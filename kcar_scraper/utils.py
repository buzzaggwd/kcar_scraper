def normalize_date(ym_str):
    if len(ym_str) == 6:
        return f"{ym_str[:4]}-{ym_str[4:]}"
    else:
        return ym_str