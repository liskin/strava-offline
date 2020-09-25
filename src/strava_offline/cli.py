from . import auth


def main():
    token = auth.get_token()
    print(token)
