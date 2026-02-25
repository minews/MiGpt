import argparse
import asyncio

from xiaogpt.config import Config
from xiaogpt.xiaogpt import MiGPT


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        dest="config",
        help="config file path",
    )
    options = parser.parse_args()

    config = Config.from_options(options)

    async def _run(config: Config) -> None:
        miboy = MiGPT(config)
        try:
            await miboy.run_forever()
        finally:
            await miboy.close()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(_run(config))


if __name__ == "__main__":
    main()
