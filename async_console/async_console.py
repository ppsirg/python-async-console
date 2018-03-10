# -*- coding: utf-8 -*-

"""Main module."""

import gi
import asyncio
import gbulb
from copy import deepcopy

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class async_console_window(Gtk.Window):
    """define console window"""
    def __init__(self, async_loop, async_queue):
        Gtk.Window.__init__(self, title='asyncio console implementation')
        self.build_interface()
        self.async_loop = async_loop
        self.q = async_queue
        self.iq = asyncio.Queue()
        self.input_event = asyncio.Event()

    def build_interface(self):
        # define ui elements
        self.main_box = Gtk.Box(spacing=6, orientation=Gtk.Orientation.VERTICAL)
        self.output_box = Gtk.Label('__ welcome to the python asyncio friendly console __')
        self.scrolled_win = Gtk.ScrolledWindow()
        self.input_buffer = Gtk.EntryBuffer()
        self.input_box = Gtk.Entry.new_with_buffer(self.input_buffer)
        # assemble ui
        self.add(self.main_box)
        self.scrolled_win.add_with_viewport(self.output_box)
        self.main_box.pack_start(self.scrolled_win, True, True, 0)
        self.main_box.pack_start(self.input_box, True, True, 0)
        # set property
        self.props.default_width = 500
        self.props.default_height = 300
        self.input_box.set_alignment = 0
        self.output_box.set_justify(Gtk.Justification.LEFT)
        # connect events with handlers
        # self.connect("delete-event", Gtk.main_quit)
        self.connect('delete-event', lambda *args: self.async_loop.stop())
        self.input_box.connect("activate", self.manage_inputs)
        # show ui
        self.listen_exports()
        self.show_all()

    def manage_inputs(self, widget):
        text = widget.get_text()
        self.log_output('user', text)
        self.input_event.set()
        self.last_input = deepcopy(text)
        widget.set_text('')

    @asyncio.coroutine
    def export(self, source, message):
        yield from self.q.put((source, message))

    @asyncio.coroutine
    def listen_exports(self):
        while True:
            source, message = yield from self.q.get()
            self.log_output(source, message)

    def log_output(self, source, message):
        new_text = '\n'.join([self.output_box.get_text(), '[{}]:_ {}'.format(source, message)])
        self.output_box.set_text(new_text)
        scroll_adj = self.scrolled_win.get_vadjustment()
        scroll_position = scroll_adj.get_upper()
        scroll_adj.set_value(scroll_position)

    @asyncio.coroutine
    def report(self, q):
        while True:
            text = yield from self.input_event.wait()
            yield from q.put(self.last_input)
            self.input_event.clear()

    @asyncio.coroutine
    def scroll_auto_adjust(self):
        last_position = 0
        refresh = 0
        while True:
            yield from asyncio.sleep(0.5)
            scroll_adj = self.scrolled_win.get_vadjustment()
            scroll_position = scroll_adj.get_upper()
            if refresh == 0:
                last_position = deepcopy(scroll_position)
                refresh += 1
                continue
            if refresh >= 1 and last_position != scroll_position:
                scroll_adj.set_value(scroll_position)



@asyncio.coroutine
def stuff(q):
    yield from asyncio.sleep(3)
    yield from q.put(('hello', 'moto'))
    print('there')


def main_async():
    gbulb.install(gtk=True)
    loop = gbulb.get_event_loop()
    q = asyncio.Queue()
    console = async_console_window(loop, q)
    asyncio.async(stuff(q))
    loop.run_forever()


if __name__ == '__main__':
    main_async()
