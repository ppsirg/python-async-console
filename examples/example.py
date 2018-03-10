import asyncio
import gbulb
from async_console.async_console import async_console_window
# from queue import Q


@asyncio.coroutine
def gui_loop(ui):
    for i in range(100):
        yield from ui.export('app', i)
        ui.log_output('app', i)
        yield from asyncio.sleep(1)


@asyncio.coroutine
def input_handler(ui):
    q = asyncio.Queue()
    asyncio.ensure_future(ui.report(q))
    asyncio.ensure_future(ui.scroll_auto_adjust())
    while True:
        number = yield from q.get()
        try:
            response = '\n'.join(['o' * i for i in range(1, int(number) + 1)])
        except Exception as e:
            response = 'not a number buddy, sorry'
        text = 'you said {}, so:\n{}'.format(number, response)
        ui.log_output('app', text)


def main_async():
    q = asyncio.Queue()
    gbulb.install(gtk=True)
    loop = gbulb.get_event_loop()
    console = async_console_window(loop, q)
    # asyncio.async(gui_loop(console
    asyncio.ensure_future(input_handler(console))
    loop.run_forever()

if __name__ == '__main__':
    main_async()
