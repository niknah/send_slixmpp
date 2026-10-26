#!/usr/bin/python3

# git clone --depth=1 https://codeberg.org/poezio/slixmpp

import sys
import os
import platform
file_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(file_path+'/slixmpp')

import argparse  # noqa: E402
import logging  # noqa: E402
import asyncio

from slixmpp import ClientXMPP  # noqa: E402


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
        self.subject = None

    def start_echo(self):
        self.add_event_handler("message", self.echo_message)

    def send_message_lines(self):
        upto = 0
        subject = args.subject
        if subject is None:
            subject = ''
        else:
            subject = subject + "\n"
        messages_count = 0
        while upto < len(self.message) and messages_count < 3:
            uptoNext = upto + 20
            s = ("".join(self.message[upto:uptoNext])).strip()
            if len(s) <= 0:
                break

            mbody = "Host: {}\n{}{}".format(
                platform.node(),
                subject,
                s
                )
            self.send_message(mto=self.dest_jid, mbody=mbody)
            upto = uptoNext
            messages_count += 1

    def session_start(self, event):
        self.send_presence()
        self.get_roster()

        if self.message is not None and self.dest_jid is not None:
            self.send_message_lines()
        self.disconnect()

    def echo_message(self, msg):
        if msg['type'] in ('chat', 'normal'):
            msg.reply("Thanks for sending\n%(body)s" % msg).send()


def start_xmpp(args):
    user = args.user
    if 'XMPP_USER' in os.environ:
        user = os.environ['XMPP_USER']
    xmpp = EchoBot(
        user,
        os.environ['XMPP_PASS']
        )
    xmpp.dest_jid = args.dest
    return xmpp





class SendMsgBot(ClientXMPP):

    """
    A basic Slixmpp bot that will log in, send a message,
    and then log out.
    """

    def __init__(self, jid, password, recipient, message):
        ClientXMPP.__init__(self, jid, password)

        # The message we wish to send, and the JID that
        # will receive it.
        self.recipient = recipient
        self.msg = message

        # The session_start event will be triggered when
        # the bot establishes its connection with the server
        # and the XML streams are ready for use. We want to
        # listen for this event so that we we can initialize
        # our roster.
        self.add_event_handler("session_start", self.start)

    async def start(self, event):
        """
        Process the session_start event.

        Typical actions for the session_start event are
        requesting the roster and broadcasting an initial
        presence stanza.

        Arguments:
            event -- An empty dictionary. The session_start
                     event does not provide any additional
                     data.
        """
        self.send_presence()
        await self.get_roster()

        self.send_message(mto=self.recipient,
                          mbody=self.msg,
                          mtype='chat')

        self.disconnect()

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
        "user",
        type=str,
        help="from jid xxx@xxmpserver.com/resource"
        )
    parser.add_argument(
        "dest",
        nargs="?",
        type=str,
        help="destination jid xxx@xxmpserver.com/resource"
        )
    parser.add_argument(
        "--subject",
        type=str,
        help="Subject of message"
        )
    parser.add_argument(
        "--address",
        type=str,
        help="server.com:port"
        )
    parser.add_argument(
        "--echo",
        action="store_true",
        help="Echo any messages received"
        )
    parser.add_argument("--verbose", action="store_true", help="Verbose")
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(levelname)-8s %(message)s'
            )

    data = sys.stdin.readlines()
    s = ("".join(data)).strip()
    if len(s) <= 0:
        exit(0)
    subject =  args.subject or ""
    message = f"{subject}\n\n{s}"

    password = os.environ['XMPP_PASS']
    xmpp = SendMsgBot(args.user, password, args.dest, message)
    xmpp.register_plugin('xep_0030') # Service Discovery
    xmpp.register_plugin('xep_0199') # XMPP Ping


    # Connect to the XMPP server and start processing XMPP stanzas.
    xmpp.connect()
    asyncio.get_event_loop().run_until_complete(xmpp.disconnected)

#    if args.echo:
#        xmpp = start_xmpp(args)
#        xmpp.start_echo()
#    else:
#        data = sys.stdin.readlines()
#        s = ("".join(data)).strip()
#        if len(s) <= 0:
#            exit(0)
#        xmpp = start_xmpp(args)
#        xmpp.message = data
#
#    if args.subject:
#        xmpp.subject = args.subject
#
#    if args.address:
#        addressArr = args.address.split(':')
#        xmpp.connect((addressArr[0], int(addressArr[1])))
#    else:
#        xmpp.connect()
#    if args.echo:
#        xmpp.process(forever=True)
#    else:
#        xmpp.process(forever=False)
