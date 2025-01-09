def strtobool(value):
    match value.lower():
        case "true" | "yes" | "y" | "on" | "1":
            return True
        case "false" | "no" | "n" | "off" | "0":
            return False
    raise ValueError
