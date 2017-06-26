import os
import logging

import gi
gi.require_version('Gtk', '3.0')
from twisted.internet import gtk3reactor
gtk3reactor.install()

from nose.twistedtools import reactor

from keysign.gpgmh import openpgpkey_from_data
from keysign.wormholeoffer import WormholeOffer
from keysign.wormholereceive import WormholeReceive
from keysign.gpgmh import get_public_key_data
from nose.tools import *


log = logging.getLogger(__name__)
thisdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.join(thisdir, "..")


def get_fixture_dir(fixture=""):
    dname = os.path.join(thisdir, "fixtures", fixture)
    return dname


def get_fixture_file(fixture):
    fname = os.path.join(get_fixture_dir(), fixture)
    return fname


def read_fixture_file(fixture):
    fname = get_fixture_file(fixture)
    data = open(fname, 'rb').read()
    return data


def stop_reactor():
    reactor.callFromThread(reactor.stop)


@timed(10)
def test_wrmhl():
    data = read_fixture_file("seckey-no-pw-1.asc")
    key = openpgpkey_from_data(data)
    file_key_data = get_public_key_data(key.fingerprint)
    log.info("Running with key %r", key)

    def check_key(downloaded_key_data):
        log.info("Checking with key: %r", key)
        assert_equal(downloaded_key_data, file_key_data)
        stop_reactor()
        return downloaded_key_data == key

    def prepare_receive(code, data):
        # Start wormhole receive with the code generated by offer
        WormholeReceive(code, check_key).start()

    # Start offering the key
    WormholeOffer(key, callback_code=prepare_receive).start()


@timed(10)
def test_wrmhl_offline_code():
    data = read_fixture_file("seckey-no-pw-1.asc")
    key = openpgpkey_from_data(data)
    code = "55-penguin-paw-print"

    def callback_receive(self, downloaded_key_data):
        file_key_data = get_public_key_data(self.key.fingerprint)
        assert_equals(file_key_data, downloaded_key_data)
        stop_reactor()

    # Start offering the key
    WormholeOffer(key, code=code).start()
    # Start receiving the key
    WormholeReceive(code, callback_receive).start()
