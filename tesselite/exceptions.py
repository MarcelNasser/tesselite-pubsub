from typing import Callable, Type

from retry import retry


def graceful(action: Callable):

    from tesselite import App

    def run(*args, **kwargs):

        try:
            return action(*args, **kwargs)
        except KeyboardInterrupt:
            App.Logger.info("bye.")
        except:
            raise

    return run




def connexion(expected_errors:tuple, noisy_errors:tuple=()):

    from tesselite import App

    def run(action:Callable):

        @retry(expected_errors+noisy_errors, delay=2, backoff=2, max_delay=20)
        def inner(*args, **kwargs):
            try:
                return action(*args, **kwargs)
            except expected_errors as err:
                App.Logger.error(f"({action.__name__}) connexion error [{err.__class__.__name__}] => backoff.")
                raise
            except noisy_errors as err:
                App.Logger.debug(f"({action.__name__}) connexion error [{err.__class__.__name__}] => backoff.")
                raise
            except KeyboardInterrupt:
                raise
            except Exception as err:
                App.Logger.error(f"({action.__name__}) unknown error => {err}")
                raise

        return inner

    return run


class MessageProcessingException(Exception):
    pass


class ConfigurationException(Exception):
    pass
