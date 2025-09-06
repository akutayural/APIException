import click

from api_exception import __version__


@click.command()
def main():
    click.secho(f"✨ APIException current latest version: v{__version__} ✨", fg="green")
    click.secho("📚 PyPI: https://pypi.org/project/APIException/", fg="blue")
    click.secho("💻 GitHub: https://github.com/akutayural/APIException", fg="cyan")
    click.secho("👤 Maintainer: Ahmet Kutay URAL", fg="yellow")
    click.echo()
    click.secho("🔑 Basic Usage Example:", fg="magenta")
    click.echo("  from api_exception import APIException, ExceptionCode, register_exception_handlers, ResponseModel")
    click.echo("  from fastapi import FastAPI")
    click.echo()
    click.echo("  app = FastAPI()")
    click.echo("  register_exception_handlers(app)")
    click.echo()
    click.echo("  @app.get('/login')")
    click.echo("  async def login(username: str, password: str):")
    click.echo("      if username != 'admin' or password != 'admin':")
    click.echo("          raise APIException(error_code=ExceptionCode.AUTH_LOGIN_FAILED, http_status_code=401)")
    click.echo("      return ResponseModel(data={'username': username})")
    click.echo()
    click.secho("🧩 Custom ExceptionCode Example:", fg="magenta")
    click.echo("  from custom_enum.enums import BaseExceptionCode")
    click.echo()
    click.echo("  class CustomExceptionCode(BaseExceptionCode):")
    click.echo("      USER_NOT_FOUND = ('USR-404', 'User not found.', 'The specified user does not exist.')")
    click.echo()
    click.echo("  @app.get('/user/{user_id}')")
    click.echo("  async def get_user(user_id: int):")
    click.echo("      if user_id != 1:")
    click.echo("          raise APIException(error_code=CustomExceptionCode.USER_NOT_FOUND, http_status_code=404)")
    click.echo("      return ResponseModel(data={'user_id': user_id, 'name': 'John Doe'})")
    click.echo()
    click.secho("Run your FastAPI app and enjoy consistent error handling! 🚀", fg="green")


if __name__ == "__main__":
    main()
