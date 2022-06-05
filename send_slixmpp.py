#!/usr/bin/python3

import sys
import os
file_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(file_path+'/slixmpp')

import argparse
import logging

from slixmpp import ClientXMPP
from slixmpp.exceptions import IqError, IqTimeout


class EchoBot(ClientXMPP):

    def __init__(self, jid, password):
        ClientXMPP.__init__(self, jid, password)

        self.add_event_handler("session_start", self.session_start)

        # If you wanted more functionality, here's how to register plugins:
        # self.register_plugin('xep_0030') # Service Discovery
        # self.register_plugin('xep_0199') # XMPP Ping

        # Here's how to access plugins once you've registered them:
        # self['xep_0030'].add_feature('echo_demo')

        # If you are working with an OpenFire server, you will
        # need to use a different SSL version:
        # import ssl
        # self.ssl_version = ssl.PROTOCOL_SSLv3
        self.dest_jid = None
        self.message = None

    def setup_echo(self):
        self.add_event_handler("message", self.message_event)

    def session_start(self, event):
        self.send_presence()
        self.get_roster()

        if self.message is not None:
            self.send_message(mto=self.dest_jid, mbody=self.message)

            self.disconnect()

        # Most get_*/set_* methods from plugins use Iq stanzas, which
        # can generate IqError and IqTimeout exceptions
        #
        # try:
        #     self.get_roster()
        # except IqError as err:
        #     logging.error('There was an error getting the roster')
        #     logging.error(err.iq['error']['condition'])
        #     self.disconnect()
        # except IqTimeout:
        #     logging.error('Server is taking too long to respond')
        #     self.disconnect()

    def message_event(self, msg):
        if msg['type'] in ('chat', 'normal'):
            msg.reply("Thanks for sending\n%(body)s" % msg).send()


if __name__ == '__main__':
    # Ideally use optparse or argparse to get JID,
    # password, and log level.
    parser = argparse.ArgumentParser(epilog="Set XMPP_PASS in the environment for the password.\n"+
            "Example: echo 'message' | ./send_slixmpp.py 'from@address.com' 'to@address.com'"
            )
    parser.add_argument("user", type=str, help="from jid xxx@xxmpserver.com/resource")
    parser.add_argument("dest", type=str, nargs="?", help="destination jid xxx@xxmpserver.com/resource")
    parser.add_argument("--echo", action="store_true", help="Echo any messages received")
    parser.add_argument("--verbose", action="store_true", help="Verbose")
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG, format='%(levelname)-8s %(message)s')

    user = args.user
    if 'XMPP_USER' in os.environ:
        user = os.environ['XMPP_USER']
    xmpp = EchoBot(user,
        os.environ['XMPP_PASS']
        )
    xmpp.dest_jid=args.dest
    if args.echo is True:
        xmpp.setup_echo()
        xmpp.connect()
        xmpp.process(forever=True)
    else:
        data = sys.stdin.readlines()
        s = ("\n".join(data)).strip()
        if len(s)<=0:
            exit(0)
        xmpp.message=s
        xmpp.connect()
        xmpp.process(forever=False)
