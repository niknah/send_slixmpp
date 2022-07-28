#!/usr/bin/python3

import sys
import argparse
import logging
import threading
import os
file_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(file_path+'/slixmpp')


from slixmpp import ClientXMPP
# from slixmpp.exceptions import IqError, IqTimeout


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
        self.add_event_handler("message", self.echo_message)

    def send_message_lines(self):
        upto = 0
        while upto < len(self.message):
            uptoNext = upto + 10
            s = ("\n".join(self.message[upto:uptoNext])).strip()
            if len(s) <= 0:
                break

            self.send_message(mto=self.dest_jid, mbody=s)
            upto = uptoNext
        self.disconnect()

    def session_start(self, event):
        self.send_presence()
        self.get_roster()

        if self.message is not None and self.dest_jid is not None:
            self.send_message_lines()
#            threading.Timer(2,self.send_message_lines).start()

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

    def echo_message(self, msg):
        if msg['type'] in ('chat', 'normal'):
            msg.reply("Thanks for sending\n%(body)s" % msg).send()


if __name__ == '__main__':
    # Ideally use optparse or argparse to get JID,
    # password, and log level.
    run_cmd = 'XMPP_PASS=xxx '+__file__
    parser = argparse.ArgumentParser(
        description="Sends message from stdin to xmpp server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='Set password with "' +
        run_cmd + '"' + "\n\n" +
        "Example...\n" +
        "echo 'message' | " + run_cmd +
        " user@xmpp.server.com touser@xmpp.server.com/*"
    )
    parser.add_argument(
            "user", type=str,
            help="from jid xxx@xxmpserver.com/resource")
    parser.add_argument(
            "dest", nargs='?', type=str,
            help="destination jid xxx@xxmpserver.com/resource")
    parser.add_argument(
            "--address", type=str,
            help="server.com:port")
    parser.add_argument(
            "--echo", action="store_true",
            help="Echo any messages received")
    parser.add_argument("--verbose", action="store_true", help="Verbose")
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(levelname)-8s %(message)s')

    user = args.user
    if 'XMPP_USER' in os.environ:
        user = os.environ['XMPP_USER']
    xmpp = EchoBot(
        user,
        os.environ['XMPP_PASS']
        )
    xmpp.dest_jid = args.dest
    if args.echo:
        xmpp.setup_echo()
    elif xmpp.dest_jid is not None:
        data = sys.stdin.readlines()
        xmpp.message = data
    else:
        print("Must mention destination address\n")
        exit(1)

    if args.address:
        addressArr = args.address.split(':')
        xmpp.connect((addressArr[0], int(addressArr[1])))
    else:
        xmpp.connect()
    if args.echo:
        xmpp.process(forever=True)
    else:
        xmpp.process(forever=False)
