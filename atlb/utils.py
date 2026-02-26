# AT PROJECT Limited 2022 - 2024; nEXT-v4.0_beta.1

def truncate_title(title, max_length=65):
    if len(title) > max_length:
        return title[:max_length - 3] + "..."
    
    return title